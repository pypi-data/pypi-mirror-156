def time_def_(func):
    """
    example:
    from time_def import time_def
    import time

    @time_def
    def time_sleep(r, r2):
        time.sleep(1)
        return r, r2

    time_sleep(1, r2=4)
    # func: time_sleep, res=(1, 4), time: 1.0127627849578857 s
    """
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(f"func: {func.__name__}, {res=}, time: {end - start} s")
        return res
    return wrapper