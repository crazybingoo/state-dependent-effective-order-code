import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / 'tools' / 'check_release.py'
spec = importlib.util.spec_from_file_location('release_guard', path)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class ReleasePolicy(unittest.TestCase):
    def test_plain_synthetic_example_allowed(self):
        self.assertEqual(guard.validate_blob('methods/demo.py', b'x = [0.1, 0.2, 0.3]\n'), [])

    def test_matrix_product_not_a_mail_address(self):
        content = b'x = B.T' + b'@' + b'np.linalg.solve(A, B)\n'
        self.assertEqual(guard.validate_blob('methods/demo.py', content), [])

    def test_contact_in_python_string_is_rejected(self):
        value = '"' + 'example' + '@' + 'example.test' + '"'
        self.assertIn('mail address', guard.validate_blob('methods/demo.py', value.encode()))

    def test_unapproved_data_path_rejected(self):
        self.assertIn('path outside reviewed allowlist', guard.validate_blob('observations.csv', b'x,y\n'))

    def test_reviewed_pseudonymous_result_allowed(self):
        columns = guard.RESULT_SCHEMAS['results/seeg_candidate_curves.csv'].replace(' ', ',')
        row = ','.join(['S' + '99', 'P' + '99', '1', 'low', '2', 'True', '0.01', '90'])
        self.assertEqual(guard.validate_blob('results/seeg_candidate_curves.csv', (columns + '\n' + row + '\n').encode()), [])

    def test_result_rejects_identity_and_extra_fields(self):
        path = 'results/seeg_candidate_curves.csv'
        columns = guard.RESULT_SCHEMAS[path].replace(' ', ',')
        row = ','.join(['S' + '99', 'P' + '99', '1', 'low', '2', 'True', '0.01', '90'])
        invalid = row.replace('P' + '99', 'a-person-name')
        self.assertIn('unapproved result value', guard.validate_blob(path, (columns + '\n' + invalid).encode()))
        self.assertIn('unapproved result schema', guard.validate_blob(path, (columns + ',extra\n' + row + ',value').encode()))

    def test_result_rejects_signal_arrays_and_nonfinite_values(self):
        path = 'results/seeg_candidate_curves.csv'
        columns = guard.RESULT_SCHEMAS[path].replace(' ', ',')
        for value in ('NaN', 'inf', 'a sequence of signal samples', '=1+1'):
            row = ','.join(['S' + '99', 'P' + '99', '1', 'low', '2', 'True', value, '90'])
            self.assertTrue(guard.validate_blob(path, (columns + '\n' + row).encode()))

    def test_archive_disguised_as_source_rejected(self):
        issues = guard.validate_blob('methods/demo.py', b'PK\x03\x04payload')
        self.assertIn('binary or archive payload', issues)

    def test_symbolic_link_rejected(self):
        self.assertIn('non-regular file', guard.validate_blob('README.md', b'private_file', '120000'))

    def test_placeholder_identifiers_rejected(self):
        for prefix in ('P', 'S', 'G'):
            content = ('label = ' + prefix + str(99)).encode()
            self.assertIn('record identifier', guard.validate_blob('methods/demo.py', content))

    def test_identifier_columns_rejected(self):
        content = ('patient' + '_' + 'id').encode()
        self.assertIn('clinical identifier field', guard.validate_blob('README.md', content))

    def test_mail_and_credentials_rejected(self):
        mail = ('example' + '@' + 'example.test').encode()
        token = ('gh' + 'p_' + 'a' * 30).encode()
        self.assertIn('mail address', guard.validate_blob('README.md', mail))
        self.assertIn('access credential', guard.validate_blob('README.md', token))

    def test_oversized_or_encoded_asset_rejected(self):
        self.assertIn('oversized text asset', guard.validate_blob('README.md', b'x ' * 50_001))
        self.assertIn('encoded payload', guard.validate_blob('README.md', b'x' * 300))


if __name__ == '__main__':
    unittest.main()
