# utils/decorators.py

import logging
from functools import wraps

_logged_functions = set()
_component_states = {}
_initialized_components = set()

def debug_log(func):
    """Decorator to log function entry/exit when debug mode is enabled"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        debug_enabled = False
        
        try:
            if args and hasattr(args[0], 'debug_var'):
                debug_enabled = args[0].debug_var.get()
            if 'debug' in kwargs:
                debug_enabled = debug_enabled or kwargs['debug']
        except (AttributeError, TypeError):
            debug_enabled = False
            
        # Skip detailed logging for periodic checks
        is_periodic = func.__name__ in ['dropdown_checker']
        
        if debug_enabled and not is_periodic:
            func_name = func.__name__
            
            try:
                result = func(*args, **kwargs)
                
                # Handle component initialization
                if 'initialize' in func_name:
                    # Skip redundant WebUtils logs
                    if 'webutils' in func_name.lower():
                        if func_name not in _initialized_components:
                            _initialized_components.add(func_name)
                            logging.debug("WebUtils initialization started")
                        return result
                    
                    # Handle tooltip initialization
                    elif 'tooltip' in func_name.lower():
                        tooltip_text = args[1] if len(args) > 1 else ''
                        if tooltip_text and tooltip_text not in _logged_functions:
                            _logged_functions.add(tooltip_text)
                            if len(tooltip_text) > 50:
                                tooltip_text = f"{tooltip_text[:47]}..."
                            logging.debug(f"Tooltip created: {tooltip_text}")
                        return result
                    
                    # Handle other component initialization
                    else:
                        component = func_name.replace('initialize_', '').split('_')[0].capitalize()
                        init_key = f"{component}_{func_name}"
                        
                        if component and init_key not in _initialized_components:
                            _initialized_components.add(init_key)
                            if component not in _component_states:
                                _component_states[component] = True
                                logging.debug(f"{component} initialization started")
                            elif 'complete' in str(args) or func_name.endswith('complete'):
                                logging.debug(f"{component} initialization complete")
                                _component_states.pop(component, None)
                
                # Log only significant state changes
                elif (func_name.endswith('complete') or 
                      (not any(x in func_name.lower() for x in 
                             ['set_', 'get_', 'display_', 'create', 'setup', 'initialize']) and
                       func_name not in _logged_functions)):
                    _logged_functions.add(func_name)
                    logging.debug(f"{func_name} completed")
                
                return result
            except Exception as e:
                logging.debug(f"Exception in {func_name}: {str(e)}")
                raise
        else:
            return func(*args, **kwargs)
    return wrapper