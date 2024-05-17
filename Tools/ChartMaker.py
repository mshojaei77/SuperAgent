import matplotlib.pyplot as plt

class ChartTool:
    def __init__(self):
        pass

    def generate_line_chart(self, x, y, title='', xlabel='', ylabel=''):
        plt.figure()
        plt.plot(x, y)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show()

    def generate_bar_chart(self, categories, values, title='', xlabel='', ylabel=''):
        plt.figure()
        plt.bar(categories, values)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show()

    def generate_scatter_plot(self, x, y, title='', xlabel='', ylabel=''):
        plt.figure()
        plt.scatter(x, y)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show()

# Example usage
if __name__ == "__main__":
    tool = ChartTool()
    tool.generate_line_chart([1, 2, 3], [4, 5, 6], "Line Chart", "X Axis", "Y Axis")
    tool.generate_bar_chart(["A", "B", "C"], [10, 20, 30], "Bar Chart", "Category", "Value")
    tool.generate_scatter_plot([1, 2, 3], [4, 5, 6], "Scatter Plot", "X Axis", "Y Axis")