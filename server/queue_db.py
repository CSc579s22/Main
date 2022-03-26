import queue
from config import QueueSize
from collections import defaultdict

# q = queue.Queue(maxsize=3)
#
# q.put("B")
# q.put("i")
# # q.put("t")
# q.put("21")
#
# # print(q.get())
#
# print(q.queue[1])
# print(q.qsize())
# print(q.full())


previous_stats_tx = queue.Queue(maxsize=QueueSize)
previous_stats_rx = queue.Queue(maxsize=QueueSize)

# db = {
#     "__dpid": {
#         "__portno": {
#             "tx": previous_stats_tx,
#             "rx": previous_stats_rx,
#         }
#     }
# }
db = defaultdict(lambda: defaultdict(lambda: defaultdict()))


def put_one(dpid, portno, stat_tx, stat_rx):
    q_tx = db[dpid][portno]["tx"]
    q_rx = db[dpid][portno]["rx"]
    if q_tx.full():
        q_tx.get()
    if q_rx.full():
        q_rx.get()
    q_tx.put(stat_tx)
    q_rx.put(stat_rx)


# get all without remove
def get_all(dpid, portno):
    q_tx = db[dpid][portno]["tx"]
    q_rx = db[dpid][portno]["rx"]
    res_tx = [res for res in q_tx.queue]
    res_rx = [res for res in q_rx.queue]
    return res_tx, res_rx


if __name__ == "__main__":
    db["sad"]["1"]["tx"] = queue.Queue(maxsize=QueueSize)
    db["sad"]["1"]["rx"] = queue.Queue(maxsize=QueueSize)
    for i in range(20):
        put_one("sad", "1", i, i + 1)
    print(get_all("sad", "1"))
