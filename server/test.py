from cache.fairness import stage1

res = [360, 360, 360, 720]
r_max = [262537, 262537, 262537, 791182]
total_bw = 1000

print(stage1(res, r_max, total_bw))
