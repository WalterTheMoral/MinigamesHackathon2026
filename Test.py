leaderboard = [2, 4, 1, 0]

sorted_leaderboard = sorted(enumerate(leaderboard), key=lambda score: score[1], reverse=True)
print(sorted_leaderboard)

print("\n".join(str(x) for x in sorted_leaderboard))

for score in sorted_leaderboard:
    print(" : ".join([str(s) for s in score]))
