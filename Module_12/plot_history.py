import matplotlib.pyplot as plt
import os

# --- Part 1: Placeholder Data Generation ---
# In a real scenario, this part would be replaced by data
# imported from your previous model training step.
#
# Since this data isn't provided, I'm generating random data
# that plausibly demonstrates the plotting code's function.
# The data in image_2.png is plotted over ~10,000 epochs.
import numpy as np

# A real 'history' object might be a dictionary from Keras or a simple python dictionary
# with list values, collected per epoch. Let's create one.
history = {}
epochs = 10000

# Generating placeholder data
# Image image_2.png shows Train MSE decreasing from roughly 0.25 to 0.22.
history['train_mse'] = np.random.uniform(0.22, 0.25, epochs)
# Ensuring it generally decreases for a better plot, similar to the image
history['train_mse'] = np.sort(history['train_mse'])[::-1]

# Generating plausible test data, which is usually slightly lower or higher
history['test_mse'] = history['train_mse'] + np.random.normal(0, 0.005, epochs)
# history['test_mse'] = np.clip(history['test_mse'], 0.21, 0.25) # Clip values
# Ensure it generally matches the overall trend
history['test_mse'] = np.sort(history['test_mse'])[::-1] + 0.005


# --- Part 2: Plotting Function ---
def plot_mse_history(collected_history, save_as='mse_curve.png'):
    """
    Plots training and test Mean Squared Error over epochs.
    Saves the plot as 'mse_curve.png'.

    Parameters:
    collected_history (dict): A dictionary containing list values for 'train_mse' and 'test_mse'.
    save_as (str): The filename to save the plot as.
    """
    # 1. Plot requirements: readable (good size)
    plt.figure(figsize=(10, 6))

    # 2. Plot requirements: training MSE versus epoch
    # and 3. test MSE versus epoch, adding labels for the legend
    plt.plot(collected_history['train_mse'], label='Train MSE')
    plt.plot(collected_history['test_mse'], label='Test MSE')

    # 4. Plot requirements: include a title
    plt.title('Train vs. Test Mean Squared Error')

    # 5. Plot requirements: include an x-axis label
    plt.xlabel('Epoch')

    # 6. Plot requirements: include a y-axis label
    plt.ylabel('MSE')

    # 7. Plot requirements: include a legend
    # and add grid for readability, matching the example
    plt.grid(True)
    plt.legend(title='variable') # Legend title matches example precisely

    # 8. Plot requirements: be clearly readable (already handled with figsize and grid)

    # 9. Plot requirements: be saved as mse_curve.png
    plt.savefig(save_as)
    print(f"Plot saved successfully as '{save_as}'.")

    # Clear the plot memory for any subsequent plotting calls
    plt.close()


# --- Part 3: Main Execution for Placeholder Demonstration ---
if __name__ == "__main__":
    # How to use with your own data:
    # 1. Un-comment the line below:
    # from your_model_module import history # Assuming your training step saves a history object

    # 2. Run the function with your real history data:
    # plot_mse_history(history)

    # For now, it will use the placeholder data generated in Part 1.
    print("Generating example MSE plot using placeholder data...")
    plot_mse_history(history)
    print("Done. Check for 'mse_curve.png' in this directory.")