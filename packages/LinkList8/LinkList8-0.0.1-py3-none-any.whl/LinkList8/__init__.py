class LinkedNode:
    def __init__(self, value):
        self.value = value
        self.next = None      

    def __repr__(self):
        return self.value
    

class LinkedList:
    def __init__(self, *values):
        self.head = None
        for value in values[::-1]:
            self.insert_at_beginning(value)
            
    def insert_at_beginning(self, value):
        current_head = self.head
        new_node = LinkedNode(value)
        new_node.next = current_head
        self.head = new_node
        
    def insert_at_end(self, value):
        if len(self) == 0:
            new_node = LinkedNode(value)
            self.head = new_node
        else:
            current_node = self.head
            while current_node:
                if not current_node.next:
                    current_tail = current_node
                    new_node = LinkedNode(value)
                    current_tail.next = new_node
                    new_node.next = None
                    break
                else:
                    current_node = current_node.next
                    
    def insert_at_index(self, index, value):
        current_node = self.head
        current_node_index = 0 
        if index == 0:
            new_node = LinkedNode(value)
            new_node.next = current_node
            self.head = new_node
        elif 1 <= index < len(self):
            while current_node:
                if current_node_index + 1 == index:
                    new_node = LinkedNode(value)
                    next_node = current_node.next
                    current_node.next = new_node
                    new_node.next = next_node
                    break
                else:
                    current_node = current_node.next
                    current_node_index += 1
        
    
    def delete_from_beginning(self):
        self.head = self.head.next
        
    def delete_from_end(self):
        current_node = self.head
        while current_node:
            if current_node.next.next == None:
                current_node.next = None
                break
            else:
                current_node = current_node.next
      
    
    def delete_value(self, value):
        current_node = self.head
        previous_node = None
        while current_node:
            if current_node.value == value:
                if previous_node == None:
                    self.head = self.head.next
                else:
                    previous_node.next = current_node.next
                return current_node.value
            else:    
                previous_node = current_node
                current_node = current_node.next
        return -1
                
    
    def search_value(self, value):
        current_node = self.head
        current_node_index = 0 
        while current_node:
            if current_node.value == value:
                return current_node_index
            else:
                current_node = current_node.next
                current_node_index += 1
        return -1
    
    
    def __repr__(self):
        values = []
        current_node = self.head
        while current_node:
            values.append(str(current_node.value))
            current_node = current_node.next
        if values:
            values.append('None')
            return ' -> '.join(values)
        else:
            return 'Linked list is empty'

    
    def __len__(self):
        count = 0
        current_node = self.head
        while current_node:
            count += 1
            current_node = current_node.next
        return count