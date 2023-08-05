# ProcessLock

**Python全局进程锁，文件锁!**

## 安装

    pip install ProcessLock

## 使用

    from ProcessLock import ProcessLock

    p_lock = ProcessLock()

    p_lock.acquire()
    try:
        # doing..
        print(p_lock.locked())
    finally:
        p_lock.release()

用法和普通的锁一样，`acquire`、`release`、`locked`，唯一的区别是这个锁不需要传参，可以通知设置锁的id来在同一机器上获取到同一把锁

进程1
```
    from ProcessLock import ProcessLock

    p_lock = ProcessLock(id="lock_name")

    p_lock.acquire()
```

进程2
```
    from ProcessLock import ProcessLock

    p_lock = ProcessLock(id="lock_name")

    # True
    print(p_lock.locked())

    # is wait
    p_lock.acquire()
```

在两个进程中因为都指定了锁的id为 `lock_name`，所以这两个变量其实是同一把锁，其中一把抢到锁，另外一个会无限等待，直到对方释放锁或者对方所在进程结束.

进程1
```
    from ProcessLock import ProcessLock

    p_lock = ProcessLock(id="lock_name")

    p_lock.acquire()
```

进程2
```
    from ProcessLock import ProcessLock

    p_nowait_lock = ProcessLock(id="lock_name", wait=False)

    # True
    print(p_nowait_lock.locked())

    # is raise AlreadyLocked Err
    p_nowait_lock.acquire()
```

如果把锁的参数 `wait` 设置为 `False` 表示获取锁的时候不进行等待，如果锁不可用直接抛出 `AlreadyLocked` 异常

这个锁除了是传统意义上的锁的作用，也是文件锁，用途之一是防止不同的程序同时操作同一文件.