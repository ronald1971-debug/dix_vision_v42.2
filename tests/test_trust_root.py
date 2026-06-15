"""Tests for Trust Root Implementation."""

import unittest
import sys
import os

# Add paths to imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from trust_root import (
    FoundationHashLifecycle,
    get_foundation_hash_lifecycle,
    FoundationHash,
    VerificationArtifact,
    TrustAnchor,
    IntegrityResult,
    HashAlgorithm,
    TrustStatus,
    LeanArtifactGenerator,
    get_artifact_generator,
    TrustAnchorManager,
    get_trust_anchor_manager,
)


class TestFoundationHashLifecycle(unittest.TestCase):
    """Test cases for foundation hash lifecycle."""

    def setUp(self):
        """Set up test fixtures."""
        self.lifecycle = get_foundation_hash_lifecycle()

    def test_singleton_lifecycle(self):
        """Test that the lifecycle is a singleton."""
        lifecycle1 = get_foundation_hash_lifecycle()
        lifecycle2 = get_foundation_hash_lifecycle()
        self.assertIs(lifecycle1, lifecycle2)

    def test_foundation_hash_generation(self):
        """Test foundation hash generation."""
        component = "test_component"
        version = "1.0.0"
        data = b"test component data for hashing"

        foundation_hash = self.lifecycle.generate_foundation_hash(
            component=component,
            version=version,
            data=data,
            algorithm=HashAlgorithm.SHA256,
        )

        self.assertIsInstance(foundation_hash, FoundationHash)
        self.assertEqual(foundation_hash.component, component)
        self.assertEqual(foundation_hash.version, version)
        self.assertEqual(foundation_hash.hash_algorithm, HashAlgorithm.SHA256)

    def test_hash_chain_integrity(self):
        """Test hash chain integrity verification."""
        component = "chain_test"
        data1 = b"first version"
        data2 = b"second version"

        # Generate first hash
        hash1 = self.lifecycle.generate_foundation_hash(
            component=component,
            version="1.0.0",
            data=data1,
        )

        # Generate second hash with previous hash
        hash2 = self.lifecycle.generate_foundation_hash(
            component=component,
            version="2.0.0",
            data=data2,
            previous_hash=hash1.hash_value,
        )

        # Verify integrity
        integrity_result = self.lifecycle.verify_system_integrity(component)

        self.assertIsInstance(integrity_result, IntegrityResult)
        self.assertTrue(integrity_result.hash_valid)
        self.assertTrue(integrity_result.chain_intact)

    def test_rollback_validation(self):
        """Test rollback validation."""
        component = "rollback_test"
        data1 = b"version 1"
        data2 = b"version 2"

        hash1 = self.lifecycle.generate_foundation_hash(
            component=component,
            version="1.0.0",
            data=data1,
        )
        hash2 = self.lifecycle.generate_foundation_hash(
            component=component,
            version="2.0.0",
            data=data2,
            previous_hash=hash1.hash_value,
        )

        # Validate rollback from hash2 to hash1
        can_rollback = self.lifecycle.rollback_validation(hash1.hash_id, hash2.hash_id)

        self.assertTrue(can_rollback)

    def test_hash_chain_retrieval(self):
        """Test hash chain retrieval."""
        component = "chain_retrieval_test"
        data = b"test data"

        hash1 = self.lifecycle.generate_foundation_hash(
            component=component,
            version="1.0.0",
            data=data,
        )
        hash2 = self.lifecycle.generate_foundation_hash(
            component=component,
            version="2.0.0",
            data=data,
            previous_hash=hash1.hash_value,
        )

        chain = self.lifecycle.get_hash_chain(component)

        self.assertEqual(len(chain), 2)
        self.assertEqual(chain[0].hash_id, hash1.hash_id)
        self.assertEqual(chain[1].hash_id, hash2.hash_id)

    def test_trust_statistics(self):
        """Test trust statistics."""
        stats = self.lifecycle.get_trust_statistics()

        self.assertIsInstance(stats, dict)
        self.assertIn("total_hashes_generated", stats)
        self.assertIn("active_hashes", stats)


class TestLeanArtifactGenerator(unittest.TestCase):
    """Test cases for lean artifact generator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = get_artifact_generator()

    def test_singleton_generator(self):
        """Test that the generator is a singleton."""
        generator1 = get_artifact_generator()
        generator2 = get_artifact_generator()
        self.assertIs(generator1, generator2)

    def test_artifact_generation(self):
        """Test lean artifact generation."""
        foundation_hash = FoundationHash(
            hash_id="test_hash_1",
            hash_value="abc123",
            hash_algorithm=HashAlgorithm.SHA256,
            component="test_component",
            version="1.0.0",
            timestamp_ns=123456789,
        )

        artifact = self.generator.generate_artifact(
            foundation_hash=foundation_hash,
            verification_method="sha256",
        )

        self.assertIsInstance(artifact, VerificationArtifact)
        self.assertEqual(artifact.hash_id, foundation_hash.hash_id)
        self.assertEqual(artifact.status, TrustStatus.VERIFIED)

    def test_artifact_retrieval(self):
        """Test artifact retrieval."""
        foundation_hash = FoundationHash(
            hash_id="test_hash_2",
            hash_value="def456",
            hash_algorithm=HashAlgorithm.SHA256,
            component="test_component",
            version="1.0.0",
            timestamp_ns=123456789,
        )

        artifact = self.generator.generate_artifact(foundation_hash=foundation_hash)

        retrieved = self.generator.get_artifact(artifact.artifact_id)

        self.assertEqual(retrieved.artifact_id, artifact.artifact_id)

    def test_artifacts_for_hash(self):
        """Test retrieving artifacts for a specific hash."""
        foundation_hash1 = FoundationHash(
            hash_id="test_hash_3a",
            hash_value="ghi789a",
            hash_algorithm=HashAlgorithm.SHA256,
            component="test_component_a",
            version="1.0.0",
            timestamp_ns=123456789,
        )

        foundation_hash2 = FoundationHash(
            hash_id="test_hash_3b",
            hash_value="ghi789b",
            hash_algorithm=HashAlgorithm.SHA256,
            component="test_component_a",
            version="1.0.0",
            timestamp_ns=123456789,
        )

        artifact1 = self.generator.generate_artifact(foundation_hash=foundation_hash1)
        artifact2 = self.generator.generate_artifact(foundation_hash=foundation_hash2)

        # Test retrieving artifacts for the first hash
        artifacts = self.generator.get_artifacts_for_hash(foundation_hash1.hash_id)

        self.assertEqual(len(artifacts), 1)  # Only one for this specific hash


class TestTrustAnchorManager(unittest.TestCase):
    """Test cases for trust anchor manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = get_trust_anchor_manager()

    def test_singleton_manager(self):
        """Test that the manager is a singleton."""
        manager1 = get_trust_anchor_manager()
        manager2 = get_trust_anchor_manager()
        self.assertIs(manager1, manager2)

    def test_anchor_registration(self):
        """Test trust anchor registration."""
        anchor = TrustAnchor(
            anchor_id="test_anchor_1",
            public_key="test_public_key_material",
            key_type="RSA",
            trust_level=0.8,
            expiry_ns=999999999999999,
            purpose="signing",
        )

        result = self.manager.register_anchor(anchor)

        self.assertTrue(result)

    def test_anchor_retrieval(self):
        """Test anchor retrieval."""
        anchor = TrustAnchor(
            anchor_id="test_anchor_2",
            public_key="test_key",
            key_type="RSA",
            trust_level=0.9,
            expiry_ns=999999999999999,
            purpose="encryption",
        )

        self.manager.register_anchor(anchor)

        retrieved = self.manager.get_anchor(anchor.anchor_id)

        self.assertEqual(retrieved.anchor_id, anchor.anchor_id)

    def test_anchor_retrieval_by_purpose(self):
        """Test retrieving anchors by purpose."""
        # Clean up any existing anchors from previous tests
        existing_signing = self.manager.get_anchors_by_purpose("signing")
        for anchor in existing_signing:
            self.manager.revoke_anchor(anchor.anchor_id)

        anchor1 = TrustAnchor(
            anchor_id="anchor_signing_1",
            public_key="key1",
            key_type="RSA",
            trust_level=0.8,
            expiry_ns=999999999999999,
            purpose="signing",
        )
        anchor2 = TrustAnchor(
            anchor_id="anchor_signing_2",
            public_key="key2",
            key_type="RSA",
            trust_level=0.7,
            expiry_ns=999999999999999,
            purpose="signing",
        )

        self.manager.register_anchor(anchor1)
        self.manager.register_anchor(anchor2)

        signing_anchors = self.manager.get_anchors_by_purpose("signing")

        self.assertEqual(len(signing_anchors), 2)

    def test_trust_level_validation(self):
        """Test trust level validation."""
        anchor = TrustAnchor(
            anchor_id="test_anchor_3",
            public_key="test_key",
            key_type="RSA",
            trust_level=0.8,
            expiry_ns=999999999999999,
            purpose="test",
        )

        self.manager.register_anchor(anchor)

        # Should pass with lower required level
        self.assertTrue(self.manager.validate_trust_level(anchor.anchor_id, 0.5))

        # Should fail with higher required level
        self.assertFalse(self.manager.validate_trust_level(anchor.anchor_id, 0.9))

    def test_anchor_revocation(self):
        """Test anchor revocation."""
        anchor = TrustAnchor(
            anchor_id="test_anchor_4",
            public_key="test_key",
            key_type="RSA",
            trust_level=0.8,
            expiry_ns=999999999999999,
            purpose="test",
        )

        self.manager.register_anchor(anchor)

        result = self.manager.revoke_anchor(anchor.anchor_id)

        self.assertTrue(result)
        self.assertIsNone(self.manager.get_anchor(anchor.anchor_id))


class TestTrustRootIntegration(unittest.TestCase):
    """Integration tests for trust root components."""

    def test_complete_trust_flow(self):
        """Test complete trust flow from hash to artifact to anchor."""
        # Generate foundation hash
        lifecycle = get_foundation_hash_lifecycle()
        foundation_hash = lifecycle.generate_foundation_hash(
            component="integration_test",
            version="1.0.0",
            data=b"integration test data",
        )

        # Generate verification artifact
        generator = get_artifact_generator()
        artifact = generator.generate_artifact(foundation_hash=foundation_hash)

        # Verify system integrity
        integrity_result = lifecycle.verify_system_integrity(foundation_hash.component)

        self.assertGreater(integrity_result.integrity_score, 0.5)


def run_tests():
    """Run all trust root tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestFoundationHashLifecycle))
    suite.addTests(loader.loadTestsFromTestCase(TestLeanArtifactGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestTrustAnchorManager))
    suite.addTests(loader.loadTestsFromTestCase(TestTrustRootIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*70)
    print("TRUST ROOT IMPLEMENTATION TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("="*70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
