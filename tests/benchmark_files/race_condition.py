"""
Benchmark Test File: Race Condition
Expected Issue: Critical concurrency issue on line 8
"""
class Counter:
    """
    Simple counter class
    WARNING: Non-thread-safe increment operation
    """
    def __init__(self):
        self.count = 0
    
    def increment(self):
        # Line 8-11 - CRITICAL: Race condition - non-atomic read-modify-write
        temp = self.count  # Read
        temp += 1          # Modify
        self.count = temp  # Write
        return self.count
    
    def get_count(self):
        return self.count

# Usage in multi-threaded context (would cause issues)
def worker(counter):
    for _ in range(1000):
        counter.increment()
