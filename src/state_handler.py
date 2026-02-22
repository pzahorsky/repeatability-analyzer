# FSM (finite state machine) App flow control

class Appstate:
    EMPTY = "empty"
    FILE_LOADED = "file_loaded"
    SUBBOARD_SELECTED = "subboard_selected"
    #COMPONENT_SELECTED = "component_selected"
    #ALGORITHM_SELECTED = "algorithm_selected"
    #SAMPLE_SELECTED = "sample_val_selected"

class StateHandler:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state = Appstate.EMPTY
    
    def file_loaded(self):
        self.state = Appstate.FILE_LOADED

    def subboard_selected(self):
        self.state = Appstate.SUBBOARD_SELECTED
        