# VSCode Flask Debugging Guide

## Setup Complete ✅

Your Flask app is now configured for seamless VSCode debugging with the following components:

- **VSCode Launch Configuration**: `.vscode/launch.json`
- **VSCode Settings**: `.vscode/settings.json`
- **Debug-Aware Flask App**: `backend/app.py`

## How to Debug Your Flask App

### Method 1: Using VSCode Debug Panel (Recommended)

1. **Set Breakpoints**:

   - Open any Python file in your Flask app
   - Click in the left gutter next to line numbers to set breakpoints
   - Red dots will appear indicating active breakpoints

2. **Start Debugging**:

   - Press `F5` or go to Run → Start Debugging
   - Select "Debug Flask App" from the dropdown
   - Your Flask app will start with debugging enabled

3. **Exercise Your Code**:

   - Use your frontend or make API calls to trigger the code paths
   - When execution hits a breakpoint, VSCode will pause and show:
     - Current variable values
     - Call stack
     - Debug console for evaluating expressions

4. **Debug Controls**:
   - `F5`: Continue execution
   - `F10`: Step over (next line)
   - `F11`: Step into (enter function calls)
   - `Shift+F11`: Step out (exit current function)
   - `Shift+F5`: Stop debugging

### Method 2: Using Command Palette

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Debug: Start Debugging"
3. Select "Debug Flask App"

## Debug Configurations Available

### "Debug Flask App"

- Standard debugging with Flask's reloader disabled
- Best for most debugging scenarios
- Automatically detects debugger and optimizes settings

### "Debug Flask App (No Reload)"

- Explicitly disables Flask reloader
- Use if you experience issues with the standard configuration
- Forces `FLASK_RUN_RELOAD=false`

## Debugging Features

### Breakpoint Types

- **Line Breakpoints**: Click in gutter or press `F9`
- **Conditional Breakpoints**: Right-click breakpoint → Edit Breakpoint
- **Logpoints**: Right-click in gutter → Add Logpoint

### Variable Inspection

- **Variables Panel**: See all local and global variables
- **Watch Panel**: Add expressions to monitor
- **Debug Console**: Evaluate Python expressions in current context

### Advanced Features

- **Exception Breakpoints**: Break when exceptions occur
- **Call Stack**: Navigate through function calls
- **Jinja Template Debugging**: Debug Flask templates (enabled with `"jinja": true`)

## Troubleshooting

### Common Issues

1. **"Module not found" errors**:

   - Ensure your Python virtual environment is activated
   - Check that VSCode is using the correct Python interpreter
   - Verify `PYTHONPATH` is set correctly in launch configuration

2. **Breakpoints not hitting**:

   - Ensure you're using the debug configuration, not just running the file
   - Check that the code path is actually being executed
   - Verify breakpoints are set on executable lines (not comments/imports)

3. **Flask reloader conflicts**:

   - Use "Debug Flask App (No Reload)" configuration
   - The app automatically detects debugger and disables reloader

4. **Port already in use**:
   - Stop any existing Flask processes
   - Check if another debug session is running

### Debug Console Commands

While debugging, you can use the Debug Console to:

```python
# Inspect variables
print(variable_name)

# Evaluate expressions
len(some_list)

# Call functions
some_function(param)

# Import modules
import pdb; pdb.set_trace()  # Traditional pdb if needed
```

## Best Practices

1. **Set Strategic Breakpoints**:

   - Place breakpoints at function entry points
   - Add breakpoints before and after critical operations
   - Use conditional breakpoints for specific scenarios

2. **Use the Variables Panel**:

   - Expand objects to inspect their properties
   - Right-click variables to copy values or set to clipboard

3. **Leverage the Call Stack**:

   - Click on different stack frames to see variable state at each level
   - Understand the execution flow leading to your breakpoint

4. **Debug Console for Testing**:
   - Test fixes before modifying code
   - Explore object properties and methods
   - Validate assumptions about data

## Example Debugging Session

1. Set a breakpoint in a route handler (e.g., in `routes/conversation_routes.py`)
2. Start debugging with `F5`
3. Make a request from your frontend or use curl:
   ```bash
   curl http://localhost:5000/api/conversations
   ```
4. When the breakpoint hits:
   - Inspect request data in Variables panel
   - Step through the code with `F10`
   - Check database queries and responses
   - Use Debug Console to test modifications

## Integration with Your Workflow

- **Normal Development**: Continue using `python app.py` as usual
- **Debugging Sessions**: Use `F5` in VSCode when you need to debug
- **Hot Reloading**: Works when not debugging, disabled during debug sessions
- **Environment**: All your existing environment variables and configuration work

Your Flask app will now provide rich debugging information whenever you need to investigate issues or understand code behavior!
