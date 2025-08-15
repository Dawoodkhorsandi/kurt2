import random
import uuid

from locust import HttpUser, between, task


class ShortenUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.created_short_codes = []

    @task(2)
    def shorten_url(self):
        # Generate a unique URL to avoid hitting the service's cache for existing URLs.
        unique_url = f"https://my-awesome-site.com/product/{uuid.uuid4()}"

        with self.client.post(
            "/shorten",
            json={"url": unique_url},
            name="/shorten",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                try:
                    short_code = response.json()["short_code"]
                    self.created_short_codes.append(short_code)
                    response.success()
                except (KeyError, TypeError):
                    response.failure("Response did not contain a valid 'short_code'")
            else:
                response.failure(
                    f"Failed to shorten URL, status: {response.status_code}"
                )

    @task(10)  # This is the most common task, with a weight of 10.
    def redirect_url(self):
        if not self.created_short_codes:
            return

        short_code = random.choice(self.created_short_codes)

        with self.client.get(
            f"/{short_code}",
            name="/{short_code}",
            allow_redirects=False,
            catch_response=True,
        ) as response:
            if response.status_code == 307:
                response.success()
            else:
                response.failure(
                    f"Redirect failed for '{short_code}',"
                    f" status: {response.status_code}"
                )

    @task(1)  # This is the least common task.
    def get_stats(self):
        if not self.created_short_codes:
            return

        short_code = random.choice(self.created_short_codes)
        self.client.get(f"/stats/{short_code}", name="/stats/{short_code}")
