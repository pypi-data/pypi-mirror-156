class tag:
    
    def __init__(self):
        self.value     = None
        self.timestamp = None
        self.quality   = None
        
    def set(self, value=None, timestamp=None, quality=None):
        self.value     = value
        self.timestamp = timestamp
        self.quality   = quality
        
class field:
    def __init__(self):
        self.tags = []

    def add_tag(self, tag_id):
        self.__setattr__(tag_id, tag())
        
    def add_tags(self, tags):
        for t in tags:
            self.add_tag(t)
            self.tags.append(t)

first_run = True
def first_execute():
    global first_run
    if first_run:
        first_run = False
        return True
    else:
        return False

def initialize_block(input_tag_list, output_tag_list):
    inputs, outputs = field(), field()
    inputs.add_tags(input_tag_list)
    outputs.add_tags(output_tag_list)
    return inputs, outputs    