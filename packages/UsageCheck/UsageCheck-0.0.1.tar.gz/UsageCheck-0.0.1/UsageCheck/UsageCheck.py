import psutil

class UsageCheck:
    def cpu_usage():
        return psutil.cpu_percent(4)

    def ram_usage():
        return psutil.virtual_memory()[2]