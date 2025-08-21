import os
def test_vne_log(arg): # optional arg
    print(os.path.basename(__file__), "test_vne_log called with:", arg)

# Register a function to use in game.
vne.Func("hello", test_vne_log)