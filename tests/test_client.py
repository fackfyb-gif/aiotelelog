import asyncio
import unittest
from urllib.parse import parse_qs

import httpx

from funstat import FunstatClient, ProblemError


class ClientTests(unittest.TestCase):
    def test_array_params_auth_and_pydantic_model(self):
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.headers["authorization"], "Bearer secret")
            query = parse_qs(request.url.query.decode())
            self.assertEqual(query["id"], ["1", "2"])
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "tech": {
                        "request_cost": 0.5,
                        "current_ballance": 99.5,
                        "request_duration": "00:00:01",
                    },
                    "data": [
                        {
                            "id": 10,
                            "title": "Group",
                            "isPrivate": False,
                            "isChannel": False,
                        }
                    ],
                },
            )

        async def run():
            transport = httpx.MockTransport(handler)
            async with FunstatClient(
                "https://api.test", "secret", http_client=httpx.AsyncClient(transport=transport)
            ) as client:
                return await client.groups.common_groups([1, 2])

        result = asyncio.run(run())
        self.assertEqual(result.data[0].id, 10)
        self.assertEqual(result.data[0].is_private, False)

    def test_problem_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(403, json={"title": "Forbidden", "status": 403})

        async def run():
            transport = httpx.MockTransport(handler)
            async with FunstatClient(
                "https://api.test", "secret", http_client=httpx.AsyncClient(transport=transport)
            ) as client:
                await client.users.stats(3)

        with self.assertRaises(ProblemError) as caught:
            asyncio.run(run())
        self.assertEqual(caught.exception.status, 403)
        self.assertEqual(caught.exception.problem.title, "Forbidden")

    def test_pagination_iterator(self):
        def handler(request: httpx.Request) -> httpx.Response:
            page = int(parse_qs(request.url.query.decode())["page"][0])
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "tech": {
                        "request_cost": 0.1,
                        "current_ballance": 99.0,
                        "request_duration": "00:00:01",
                    },
                    "data": [{"messageId": page, "date": "2026-01-01T00:00:00Z", "text": "x",
                              "group": {"id": 1, "title": "g", "isPrivate": False}}],
                    "paging": {"total": 2, "currentPage": page, "pageSize": 1, "totalPages": 2},
                },
            )

        async def run():
            transport = httpx.MockTransport(handler)
            async with FunstatClient(
                "https://api.test", "secret", http_client=httpx.AsyncClient(transport=transport)
            ) as client:
                return [item async for item in client.users.iter_messages(5, page_size=1)]

        result = asyncio.run(run())
        self.assertEqual([item.message_id for item in result], [1, 2])

    def test_page_validation(self):
        async def run():
            async with FunstatClient("https://api.test", "secret") as client:
                await client.text.search("hello", 0, 10)

        with self.assertRaises(ValueError):
            asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
