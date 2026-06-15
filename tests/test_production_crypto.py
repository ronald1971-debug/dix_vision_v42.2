"""Tests for Production-Grade Components."""

import unittest
import sys
import os

# Add paths to imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from trust_root.production_crypto import (
    ProductionHashGenerator,
    ProductionSignatureOperations,
    ProductionKeyDerivation,
    ProductionEncryption,
    ProductionTrustRoot,
    get_production_trust_root,
    CRYPTOGRAPHY_AVAILABLE,
)


class TestProductionCrypto(unittest.TestCase):
    """Test cases for production cryptographic operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.hash_generator = ProductionHashGenerator()

    def test_sha256_hash_generation(self):
        """Test real SHA-256 hash generation."""
        data = b"test data for hashing"
        hash_value = self.hash_generator.generate_sha256_hash(data)

        self.assertIsInstance(hash_value, str)
        self.assertEqual(len(hash_value), 64)  # SHA-256 produces 64 hex characters
        self.assertTrue(all(c in '0123456789abcdef' for c in hash_value))

    def test_sha3_256_hash_generation(self):
        """Test real SHA3-256 hash generation."""
        data = b"test data for hashing"
        hash_value = self.hash_generator.generate_sha3_256_hash(data)

        self.assertIsInstance(hash_value, str)
        self.assertEqual(len(hash_value), 64)  # SHA3-256 produces 64 hex characters

    def test_hmac_generation(self):
        """Test real HMAC generation."""
        key = b"secret_key"
        data = b"test data"
        hmac_value = self.hash_generator.generate_hmac(key, data)

        self.assertIsInstance(hmac_value, str)
        self.assertEqual(len(hmac_value), 64)

    def test_hash_consistency(self):
        """Test hash consistency (same input produces same hash)."""
        data = b"consistent test data"
        hash1 = self.hash_generator.generate_sha256_hash(data)
        hash2 = self.hash_generator.generate_sha256_hash(data)

        self.assertEqual(hash1, hash2)

    def test_hash_uniqueness(self):
        """Test hash uniqueness (different input produces different hash)."""
        data1 = b"data one"
        data2 = b"data two"
        hash1 = self.hash_generator.generate_sha256_hash(data1)
        hash2 = self.hash_generator.generate_sha256_hash(data2)

        self.assertNotEqual(hash1, hash2)


@unittest.skipIf(not CRYPTOGRAPHY_AVAILABLE, "cryptography library not available")
class TestProductionSignatureOperations(unittest.TestCase):
    """Test cases for production signature operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.signature_ops = ProductionSignatureOperations()

    def test_rsa_key_pair_generation(self):
        """Test real RSA key pair generation."""
        private_key, public_key = self.signature_ops.generate_rsa_key_pair(key_size=2048)

        self.assertIsInstance(private_key, str)
        self.assertIsInstance(public_key, str)
        self.assertIn("-----BEGIN PRIVATE KEY-----", private_key)
        self.assertIn("-----BEGIN PUBLIC KEY-----", public_key)

    def test_data_signing(self):
        """Test real data signing."""
        private_key, public_key = self.signature_ops.generate_rsa_key_pair()
        data = b"test data to sign"

        signature = self.signature_ops.sign_data(private_key, data)

        self.assertIsInstance(signature, str)
        self.assertTrue(len(signature) > 0)

    def test_signature_verification(self):
        """Test real signature verification."""
        private_key, public_key = self.signature_ops.generate_rsa_key_pair()
        data = b"test data to sign"

        signature = self.signature_ops.sign_data(private_key, data)
        is_valid = self.signature_ops.verify_signature(public_key, data, signature)

        self.assertTrue(is_valid)

    def test_signature_verification_invalid(self):
        """Test signature verification with invalid signature."""
        private_key, public_key = self.signature_ops.generate_rsa_key_pair()
        data = b"test data to sign"
        wrong_data = b"wrong data"

        signature = self.signature_ops.sign_data(private_key, data)
        is_valid = self.signature_ops.verify_signature(public_key, wrong_data, signature)

        self.assertFalse(is_valid)


@unittest.skipIf(not CRYPTOGRAPHY_AVAILABLE, "cryptography library not available")
class TestProductionEncryption(unittest.TestCase):
    """Test cases for production encryption."""

    def setUp(self):
        """Set up test fixtures."""
        self.encryption = ProductionEncryption()

    def test_key_derivation(self):
        """Test real key derivation from password."""
        password = "test_password"
        salt = ProductionKeyDerivation.generate_secure_salt()

        key = ProductionKeyDerivation.derive_key_from_password(password, salt)

        self.assertIsInstance(key, bytes)
        self.assertEqual(len(key), 32)  # 256-bit key

    def test_secure_salt_generation(self):
        """Test secure random salt generation."""
        salt = ProductionKeyDerivation.generate_secure_salt()

        self.assertIsInstance(salt, bytes)
        self.assertEqual(len(salt), 32)
        # Ensure salts are different
        salt2 = ProductionKeyDerivation.generate_secure_salt()
        self.assertNotEqual(salt, salt2)

    def test_data_encryption(self):
        """Test real AES-GCM encryption."""
        key = b"01234567890123456789012345678901"  # 32-byte key
        data = b"sensitive data to encrypt"

        nonce, ciphertext, tag = self.encryption.encrypt_data(key, data)

        self.assertEqual(len(nonce), 12)  # GCM nonce is 12 bytes
        self.assertTrue(len(ciphertext) > 0)
        self.assertEqual(len(tag), 16)  # GCM tag is 16 bytes

    def test_data_decryption(self):
        """Test real AES-GCM decryption."""
        key = b"01234567890123456789012345678901"  # 32-byte key
        data = b"sensitive data to encrypt"

        nonce, ciphertext, tag = self.encryption.encrypt_data(key, data)
        decrypted_data = self.encryption.decrypt_data(key, nonce, ciphertext, tag)

        self.assertEqual(decrypted_data, data)


class TestProductionTrustRoot(unittest.TestCase):
    """Test cases for production trust root."""

    def setUp(self):
        """Set up test fixtures."""
        self.trust_root = get_production_trust_root()

    def test_register_trust_anchor(self):
        """Test registering production trust anchor."""
        anchor = self.trust_root.register_production_trust_anchor(
            anchor_id="test_anchor_1",
            purpose="signing",
            key_type="RSA",
            key_size=2048
        )

        self.assertIn("anchor_id", anchor)
        self.assertEqual(anchor["anchor_id"], "test_anchor_1")
        self.assertEqual(anchor["status"], "active")

    def test_create_foundation_hash(self):
        """Test creating production foundation hash."""
        component = "test_component"
        version = "1.0.0"
        data = b"test component data"

        foundation_hash = self.trust_root.create_production_foundation_hash(
            component=component,
            version=version,
            data=data
        )

        self.assertIn("hash_id", foundation_hash)
        self.assertIn("hash_value", foundation_hash)
        self.assertEqual(foundation_hash["component"], component)

    def test_create_verification_artifact(self):
        """Test creating production verification artifact."""
        # First register an anchor
        anchor = self.trust_root.register_production_trust_anchor(
            anchor_id="test_anchor_2",
            purpose="verification",
            key_type="RSA",
            key_size=2048
        )

        # Create foundation hash
        foundation_hash = self.trust_root.create_production_foundation_hash(
            component="test_component",
            version="1.0.0",
            data=b"test data"
        )

        # Create verification artifact
        artifact = self.trust_root.create_production_verification_artifact(
            foundation_hash=foundation_hash,
            anchor_id="test_anchor_2"
        )

        self.assertIn("artifact_id", artifact)
        self.assertIn("signature", artifact)
        self.assertEqual(artifact["status"], "verified")

    def test_verify_artifact(self):
        """Test verifying production artifact."""
        # Register anchor and create artifact
        anchor = self.trust_root.register_production_trust_anchor(
            anchor_id="test_anchor_3",
            purpose="verification_test",
            key_type="RSA",
            key_size=2048
        )

        foundation_hash = self.trust_root.create_production_foundation_hash(
            component="test_component",
            version="1.0.0",
            data=b"test data"
        )

        artifact = self.trust_root.create_production_verification_artifact(
            foundation_hash=foundation_hash,
            anchor_id="test_anchor_3"
        )

        # Verify artifact
        is_valid = self.trust_root.verify_production_artifact(artifact)

        self.assertTrue(is_valid)

    def test_trust_statistics(self):
        """Test production trust root statistics."""
        # Register some anchors
        self.trust_root.register_production_trust_anchor("anchor_1", "purpose1", "RSA")
        self.trust_root.register_production_trust_anchor("anchor_2", "purpose2", "ECDSA")

        stats = self.trust_root.get_production_trust_statistics()

        self.assertGreater(stats["total_trust_anchors"], 0)
        self.assertIn("cryptographic_operations_available", stats)


def run_production_tests():
    """Run all production component tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestProductionCrypto))
    suite.addTests(loader.loadTestsFromTestCase(TestProductionSignatureOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestProductionEncryption))
    suite.addTests(loader.loadTestsFromTestCase(TestProductionTrustRoot))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*70)
    print("PRODUCTION COMPONENT TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    if not CRYPTOGRAPHY_AVAILABLE:
        print("Note: Some tests skipped because cryptography library is not available")
    print("="*70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_production_tests()
    sys.exit(0 if success else 1)
