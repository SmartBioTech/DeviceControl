def mean(data):
    return sum(data)/len(data)


def median(data):
    data.sort()
    length = len(data)
    if length % 2 == 0:
        return (data[length // 2] + data[length // 2 - 1]) / 2
    else:
        return data[length // 2]
