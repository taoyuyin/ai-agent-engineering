import unittest

from prompt_runtime import PromptRegistry, PromptTemplate


def prompt(version="1"):
    return PromptTemplate("p", version, "system", "Hello {name}", ("name",), {"answer": "string"})


class PromptRegistryTest(unittest.TestCase):
    def test_render_has_version_and_checksum(self):
        registry = PromptRegistry()
        registry.register(prompt(), activate=True)
        result = registry.render("p", {"name": "Ada"})
        self.assertIn("Hello Ada", result.text)
        self.assertEqual("1", result.metadata["prompt_version"])
        self.assertEqual(16, len(result.metadata["prompt_checksum"]))

    def test_rejects_variable_drift_and_mutation(self):
        registry = PromptRegistry()
        registry.register(prompt())
        with self.assertRaises(ValueError):
            registry.render("p", {})
        with self.assertRaises(ValueError):
            registry.register(prompt())

    def test_canary_version_does_not_replace_active_until_activation(self):
        registry = PromptRegistry()
        registry.register(prompt("1"), activate=True)
        registry.register(prompt("2"))
        self.assertEqual("1", registry.render("p", {"name": "A"}).metadata["prompt_version"])
        registry.activate("p", "2")
        self.assertEqual("2", registry.render("p", {"name": "A"}).metadata["prompt_version"])


if __name__ == "__main__":
    unittest.main()
