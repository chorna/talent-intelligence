from django.test import TestCase


class HealthTest(TestCase):
    def test_health(self):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
            },
        )
