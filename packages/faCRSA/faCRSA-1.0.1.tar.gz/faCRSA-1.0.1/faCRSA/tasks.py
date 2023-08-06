from taskQueue import huey


@huey.task()
def submit_task(uid, tid):
    web_action(uid, tid, 0)
    return tid


from facrsa_code.library.analysis.main import web_action
