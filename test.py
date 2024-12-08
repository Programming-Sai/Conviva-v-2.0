from llm_processing import say, ai_function_execution, available_functions, tools


user_prompt = input(">> ")

# First attempt

r = ai_function_execution(user_prompt, tools, available_functions)
print(r)


# Second attempt
def show_model_response(user_prompt, speech, text):
        response = ai_function_execution(user_prompt, tools, available_functions)
        
        print(response)
   

# show_model_response(user_prompt, False, True)
