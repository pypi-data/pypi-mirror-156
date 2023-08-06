import pythonagent.agent as agent
_agent = agent.get_agent_instance()

def printhey():
    print("hello from cavisson wrapper")

def intrumentationdecorator(func):
    print("func inside decorator", func)
    print(func.__module__)
    fqm = str(func.__module__) +"."+ str(func.__name__)
    bt = _agent.get_current_bt()
    #bt = "000001"
    def inner(*args, **kwargs):
        print("dir for function to instrument",dir(fqm))
        _agent.method_entry(bt, fqm)
        func(*args, **kwargs)
        _agent.method_exit(bt, fqm, 200)
    return inner