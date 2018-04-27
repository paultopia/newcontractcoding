from testhelperclasses import *
import concurrent.futures

def firstcontract(response):
    return "a (very short)" in response["content"]

def secondcontract(response):
    return "another (very short" in response["content"]

headers=make_auth_header("gowder", "secret")

def get_root_page(self):
    response = self.client.get("/", headers=headers)
    return {"type": "root page", "content": str(response.data)}

def post_first_contract(self):
    response = self.client.post("/enter-data", headers=headers,
                               data={"1": "no",
                                     "2": "yes",
                                     "contract_id": "1"})
    return {"type": "post", "content": str(response.data)}

class TestSyncUpdate(TestStateful):
    """confirm that when run synchronously, user who fetches
    one contract and submits it gets new contract on
    next fetch, not old contract again.
    """
    def test_sync(self):
        firstpage = get_root_page(self)
        self.assertTrue(firstcontract(firstpage))
        self.assertFalse(secondcontract(firstpage))
        post = post_first_contract(self)
        secondpage = get_root_page(self)
        self.assertTrue(secondcontract(secondpage))
        self.assertFalse(firstcontract(secondpage))

class TestThreadedUpdate(TestStateful):
    def test_threads(self):
        """this is supposed to catch my race condition but it isn't,
        maybe because there isn't one?  anyway, it passes, but
        I was hoping it would fail.
        """
        firstpage = get_root_page(self)
        self.assertTrue(firstcontract(firstpage))
        self.assertFalse(secondcontract(firstpage))
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        for f in concurrent.futures.as_completed([pool.submit(post_first_contract, self), pool.submit(get_root_page, self)]):
            res = f.result()
            if res["type"] == "root page":
                self.assertTrue(secondcontract(res))
                self.assertFalse(firstcontract(res))


