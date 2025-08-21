def test_vne_log(arg): # optional arg
  print(arg)
  vne.Log("Hello, World from Python!")


# Register a function to use in game.
vne.func("hello", test_vne_log)