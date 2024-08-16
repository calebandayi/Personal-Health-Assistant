import tkinter as tk
from tkinter import messagebox
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from tkinter import filedialog
import csv

# Define default colors and themes
DEFAULT_THEME = {
    "bg": "white",
    "fg": "black",
    "button_bg": "#4CAF50",  # Green
    "button_fg": "white"
}

ALTERNATE_THEME = {
    "bg": "#263238",  # Dark blue-gray
    "fg": "white",
    "button_bg": "#FF5722",  # Deep orange
    "button_fg": "white"
}

DIET_ADVICE = {
    "Underweight": {
        "Male": {
            "Normal": "Focus on nourishing your body with nutrient-rich foods that can help you gain healthy weight. Consider increasing your calorie intake by incorporating foods such as nuts, seeds, avocados, whole grains, lean proteins like chicken, fish, tofu, and legumes into your diet. Additionally, prioritize regular meals and snacks throughout the day to support weight gain.",
            "Body Builder": "As a male bodybuilder who is underweight, focus on increasing your calorie intake with nutrient-dense foods to support muscle growth. Include a balance of protein, carbohydrates, and healthy fats in your meals. Consider incorporating foods such as lean meats, eggs, dairy, whole grains, fruits, and vegetables. Additionally, prioritize strength training exercises to build muscle mass."
        },
        "Female": {
            "Normal": "Focus on nourishing your body with nutrient-rich foods that can help you gain healthy weight. Consider increasing your calorie intake by incorporating foods such as nuts, seeds, avocados, whole grains, lean proteins like chicken, fish, tofu, and legumes into your diet. Additionally, prioritize regular meals and snacks throughout the day to support weight gain.",
            "Body Builder": {
                "Normal": "As a female bodybuilder who is underweight, focus on increasing your calorie intake with nutrient-dense foods to support muscle growth. Include a balance of protein, carbohydrates, and healthy fats in your meals. Consider incorporating foods such as lean meats, eggs, dairy, whole grains, fruits, and vegetables. Additionally, prioritize strength training exercises to build muscle mass.",
                "Expectant": "As you prepare for motherhood, prioritize your health and your baby's well-being. If you're into bodybuilding, focus on nourishing foods like nuts, lean proteins,seeds, avocados, dairy and whole grains. Stay energized with regular meals and snacks. And remember, consulting your healthcare provider can offer tailored advice for a healthy pregnancy journey.",
            },
            "Expectant": "As an expectant female, it's important to focus on gaining weight in a healthy manner to support both your own health and the health of your baby. Incorporate nutrient-dense foods such as nuts, seeds, avocados, lean proteins, whole grains, and dairy into your diet. Aim to eat regular meals and snacks to ensure you're meeting your increased calorie needs during pregnancy. Consult with a healthcare provider or dietitian for personalized guidance."
        }
    },
    "Normal weight": {
        "Male": {
            "Normal": "Maintaining a balanced diet is key to sustaining your current healthy weight. Ensure you're consuming a variety of fruits, vegetables, whole grains, and lean proteins such as poultry, fish, beans, and lentils. Aim for a balanced plate at each meal, focusing on portion control and including foods from all food groups. Remember to stay hydrated by drinking plenty of water throughout the day.",
            "Body Builder": "As a male bodybuilder with a normal weight, focus on maintaining your current weight while supporting muscle growth and performance. Consume a balanced diet that includes a mix of lean proteins, complex carbohydrates, healthy fats, fruits, and vegetables. Consider timing your meals around your workouts to optimize energy levels and recovery.",
        },
        "Female": {
            "Normal": "Maintaining a balanced diet is key to sustaining your current healthy weight. Ensure you're consuming a variety of fruits, vegetables, whole grains, and lean proteins such as poultry, fish, beans, and lentils. Aim for a balanced plate at each meal, focusing on portion control and including foods from all food groups. Remember to stay hydrated by drinking plenty of water throughout the day.",
            "Body Builder": {
                "Normal": "As a female bodybuilder with a normal weight, focus on maintaining your current weight while supporting muscle growth and performance. Consume a balanced diet that includes a mix of lean proteins, complex carbohydrates, healthy fats, fruits, and vegetables. Consider timing your meals around your workouts to optimize energy levels and recovery.",
                "Expectant": "As a bodybuilder with a normal weight who is expecting, continue to prioritize a balanced diet that supports both your health and the health of your baby. Ensure you're consuming a variety of nutrient-dense foods including fruits, vegetables, whole grains, lean proteins, and healthy fats. Stay hydrated and consult with your healthcare provider for personalized nutrition recommendations during pregnancy.",
            },
            "Expectant": "As an expectant female with a normal weight, prioritize a diet rich in nutrients crucial for pregnancy, such as folate, calcium, iron, and omega-3 fatty acids. Include foods like leafy greens, dairy products, lean meats, fish, nuts, and seeds. Aim for regular, balanced meals and snacks to provide steady energy throughout the day. Consult with your healthcare provider for personalized dietary recommendations to support a healthy pregnancy."
        }
    },
    "Overweight": {
        "Male": {
            "Normal": "It is important to focus on making gradual, sustainable changes to your diet and lifestyle. Start by incorporating more whole, nutrient-dense foods like fruits, vegetables, lean proteins, and whole grains into your meals. Practice portion control and limit your intake of processed foods, sugary snacks, and high-calorie beverages.",
            "Body Builder": "As a male bodybuilder who is overweight, focus on creating a calorie deficit through a combination of diet and exercise to support fat loss while maintaining muscle mass. Incorporate plenty of lean proteins, fruits, vegetables, and whole grains into your meals while reducing your intake of high-calorie foods and sugary snacks. Prioritize strength training to preserve muscle mass during weight loss."
        },
        "Female": {
            "Normal": "It is important to focus on making gradual, sustainable changes to your diet and lifestyle. Start by incorporating more whole, nutrient-dense foods like fruits, vegetables, lean proteins, and whole grains into your meals. Practice portion control and limit your intake of processed foods, sugary snacks, and high-calorie beverages.",
            "Body Builder": {
                "Normal": "As a female bodybuilder who is overweight, focus on creating a calorie deficit through a combination of diet and exercise to support fat loss while maintaining muscle mass. Incorporate plenty of lean proteins, fruits, vegetables, and whole grains into your meals while reducing your intake of high-calorie foods and sugary snacks. Prioritize strength training to preserve muscle mass during weight loss.",
                "Expectant": "As a bodybuilder who is overweight and expecting, it's important to focus on gaining weight in a healthy manner to support both your own health and the health of your baby. Aim to make gradual, sustainable changes to your diet by incorporating more whole, nutrient-dense foods while reducing your intake of processed foods, sugary snacks, and high-calorie beverages. Consult with a healthcare provider or dietitian for personalized guidance.",
            },
            "Expectant": "As an expectant female who is overweight, it is important to focus on making gradual, sustainable changes to your diet and lifestyle to support both your health and the health of your baby. Incorporate more whole, nutrient-dense foods like fruits, vegetables, lean proteins, and whole grains into your meals. Practice portion control and limit your intake of processed foods, sugary snacks, and high-calorie beverages. Consult with a healthcare provider or dietitian for personalized guidance during pregnancy."
        }
    },
    "Obese": {
        "Male": {
            "Normal": "As an obese male seeking to improve health, focus on a balanced diet rich in fruits, vegetables, lean proteins, and whole grains while reducing intake of high-calorie processed foods. Emphasize portion control and consider meal planning to support weight loss goals.",
            "Body Builder": "As a male bodybuilder who is obese, prioritize seeking support from healthcare professionals or registered dietitians who can provide personalized guidance and support. Together, you can develop a comprehensive meal plan tailored to your specific dietary needs and weight loss goals. Focus on incorporating plenty of fruits, vegetables, lean proteins, and whole grains into your diet while reducing your intake of high-calorie, processed foods.",
        },
        "Female": {
            "Normal": "As an obese female focused on health improvement, emphasize a balanced diet with plenty of fruits, vegetables, lean proteins, and whole grains while minimizing high-calorie processed foods. Practice portion control and consider meal planning to support weight loss efforts.",
            "Body Builder": {
                "Normal": "As a female bodybuilder who is obese, prioritize seeking support from healthcare professionals or registered dietitians who can provide personalized guidance and support. Together, you can develop a comprehensive meal plan tailored to your specific dietary needs and weight loss goals. Focus on incorporating plenty of fruits, vegetables, lean proteins, and whole grains into your diet while reducing your intake of high-calorie, processed foods.",
                "Expectant": "As a bodybuilder who is obese and expecting, it's important to focus on gaining weight in a healthy manner to support both your own health and the health of your baby. Seek support from healthcare professionals or registered dietitians who can provide personalized guidance and support. Together, you can develop a comprehensive meal plan tailored to your specific dietary needs and weight loss goals. Focus on incorporating plenty of fruits, vegetables, lean proteins, and whole grains into your diet while reducing your intake of high-calorie, processed foods.",
            },
            "Expectant": "As an expectant female considered obese,it is important to focus on a balanced diet that supports both your health and the health of your baby. Aim to consume a variety of nutrient-dense foods including fruits, vegetables, lean proteins, whole grains, and healthy fats. Practice portion control and limit your intake of processed foods, sugary snacks, and high-calorie beverages. Ensure you stay hydrated by drinking plenty of water throughout the day. While it's beneficial to consult with healthcare professionals, focusing on a healthy diet can be a positive step in managing weight during pregnancy."
        }
    }
}

BMI_CATEGORIES = {
    "Underweight": {"color": "#FF6347",}, 
    "Normal weight": {"color": "#32CD32"}, "Overweight": {"color": "#FFD700"}, "Obese": {"color": "#FF4500"}
    }

BMI_VALUES = [18.5, 24.9, 29.9, 40]  # BMI values corresponding to Underweight, Normal weight, Overweight, and Obese categories respectively
BMI_COLORS = ["#FF6347", "#32CD32", "#FFD700", "#FF4500"]

EXERCISE_PLANS = {
    "Underweight": {
        "Male": {
            "Normal": "It is important to start with low-intensity exercises to build a solid foundation of fitness. Begin by incorporating activities such as brisk walking, light jogging, or cycling into your routine for at least 30 minutes a day, 3 times a week. Focus on maintaining a comfortable pace and gradually increasing the duration and intensity of your workouts as you build stamina and confidence.",
            "Body Builder": "As an underweight male bodybuilder, start with a combination of strength training and cardiovascular exercises. Incorporate exercises using your body weight or light weights for 30-45 minutes, 3-4 times a week. Focus on compound movements like squats, deadlifts, bench presses, and rows to build overall strength and muscle mass.",
        },
        "Female": {
            "Normal": "It is important to start with low-intensity exercises to build a solid foundation of fitness. Begin by incorporating activities such as brisk walking, light jogging, or cycling into your routine for at least 30 minutes a day, 3 times a week. Focus on maintaining a comfortable pace and gradually increasing the duration and intensity of your workouts as you build stamina and confidence.",
            "Body Builder": {
                "Normal": "As a female bodybuilder who is considered underweight, start with a combination of strength training and cardiovascular exercises. Incorporate exercises using your body weight or light weights for 30-45 minutes, 3-4 times a week. Focus on compound movements like squats, deadlifts, bench presses, and rows to build overall strength and muscle mass.",
                "Expectant": "As an expectant female bodybuilder who is underweight, focus on low-impact exercises that support muscle strength and overall well-being. Engage in activities such as prenatal yoga, swimming, or light resistance training with proper guidance from a qualified instructor. Prioritize exercises that improve flexibility, posture, and pelvic floor strength to prepare for childbirth.",
            },
            "Expectant": "As an expectant female who is underweight, focus on exercises that promote overall well-being and prepare your body for childbirth. Engage in low-impact activities such as prenatal yoga, swimming, or walking, ensuring you have proper guidance from a qualified instructor. These exercises can help improve flexibility, posture, and muscle tone, which are beneficial during pregnancy and delivery. Listen to your body and avoid activities that cause discomfort or strain. Prioritize staying active to support your health and the health of your baby."
        },
    },
    "Normal weight": {
        "Male": {
            "Normal":"For maintaining a normal weight, prioritize a balanced exercise routine. Aim for cardiovascular activities like brisk walking or cycling 3-5 times a week for 30 minutes, gradually increasing intensity. Incorporate strength training 2-3 times weekly to build lean muscle mass. Daily flexibility exercises such as stretching and yoga enhance mobility and prevent injury. Stay active throughout the day by integrating physical activity into daily routines.",
            "Body Builder": "Incorporate a combination of strength training and cardiovascular exercises into your routine. Focus on compound movements like squats, deadlifts, bench presses, and rows to build overall strength and muscle mass. Additionally, include cardiovascular activities such as running, cycling, or swimming to improve endurance and overall fitness.",
        },
        "Female": {
            "Normal": "As a female aiming to maintain a healthy weight, a balanced exercise plan is essential. Incorporate cardiovascular activities such as brisk walking, jogging, or cycling 3-5 times per week for at least 30 minutes to boost metabolism and burn calories. Integrate strength training exercises targeting major muscle groups 2-3 times weekly using moderate to heavy weights to build and tone muscle, promoting a lean physique. Include flexibility exercises like yoga or Pilates daily to improve mobility and prevent injury. Stay active throughout the day by incorporating movement into daily routines. Remember to consult with a healthcare professional before starting any new exercise program.",
            "Body Builder": {
                "Normal": "Incorporate a combination of strength training and cardiovascular exercises into your routine. Focus on compound movements like squats, deadlifts, bench presses, and rows to build overall strength and muscle mass. Additionally, include cardiovascular activities such as running, cycling, or swimming to improve endurance and overall fitness.",
                "Expectant": "Continue with your regular exercise routine as long as it feels comfortable. Focus on low-impact activities such as walking, swimming, or prenatal yoga to maintain strength and flexibility. Listen to your body and consult with your healthcare provider for any modifications to your exercise routine during pregnancy.",
            },
            "Expectant": "As an expectant female aiming to maintain a healthy weight, it's essential to focus on exercises that support your overall well-being and are safe during pregnancy. Incorporate low-impact activities such as walking, swimming, or prenatal yoga into your routine to maintain strength and flexibility. Listen to your body and avoid exercises that cause discomfort or strain. Remember to consult with your healthcare provider for any modifications to your exercise routine during pregnancy. Prioritize staying active to support your health and the health of your baby."
        }
    },
    "Overweight": {
        "Male": {
            "Normal": "It is important to focus on making gradual, sustainable changes to your diet and lifestyle. Start by incorporating more whole, nutrient-dense foods like fruits, vegetables, lean proteins, and whole grains into your meals. Practice portion control and limit your intake of processed foods, sugary snacks, and high-calorie beverages.",
            "Body Builder": "As an intermediate male bodybuilder, focus on a combination of strength training and cardiovascular exercises to support fat loss and muscle growth. Incorporate compound movements like squats, deadlifts, bench presses, and rows into your routine. Additionally, include cardiovascular activities such as running, cycling, or HIIT to boost calorie burn and improve overall fitness.",
        },
        "Female": {
            "Normal": "It is important to focus on making gradual, sustainable changes to your diet and lifestyle. Start by incorporating more whole, nutrient-dense foods like fruits, vegetables, lean proteins, and whole grains into your meals. Practice portion control and limit your intake of processed foods, sugary snacks, and high-calorie beverages.",
            "Body Builder": {
                "Normal": "As a female bodybuilder, focus on a combination of strength training and cardiovascular exercises to support fat loss and muscle growth. Incorporate compound movements like squats, deadlifts, bench presses, and rows into your routine. Additionally, include cardiovascular activities such as running, cycling, or HIIT to boost calorie burn and improve overall fitness.",
                "Expectant": "As an expectant female bodybuilder who is overweight, focus on staying active with low-impact exercises that support overall fitness and well-being. Engage in activities such as swimming, prenatal yoga, or stationary cycling to maintain cardiovascular health and muscle strength. Listen to your body and consult with your healthcare provider for any modifications to your exercise routine during pregnancy.",
            },
            "Expectant": "It is important to focus on staying active with exercises that support overall fitness and well-being during pregnancy. Engage in low-impact activities such as swimming, prenatal yoga, or stationary cycling to maintain cardiovascular health and muscle strength. Listen to your body and avoid exercises that cause discomfort or strain. Prioritize staying active to support your health and the health of your baby."
        },
    },
    "Obese": {
        "Male": {
            "Normal": "Being a male considered obese, it is crucial to seek support from healthcare professionals or registered dietitians who can provide personalized guidance and support. Together, you can develop a comprehensive exercise plan tailored to your fitness level and weight loss goals. Incorporate a mix of cardiovascular exercises, strength training, and flexibility exercises to improve overall fitness and support weight loss.",
            "Body Builder": "Being a male bodybuilder considered obese, focus on high-intensity workouts that challenge your body and support fat loss. Incorporate activities such as high-intensity interval training (HIIT), circuit training, or sports activities for 45-60 minutes, 4-5 times a week. Work with a fitness professional to ensure proper form and technique.",
        },
        "Female": {
            "Normal": "It is crucial to seek support from healthcare professionals or registered dietitians who can provide personalized guidance and support. Together, you can develop a comprehensive exercise plan tailored to your fitness level and weight loss goals. Incorporate a mix of cardiovascular exercises, strength training, and flexibility exercises to improve overall fitness and support weight loss.",
            "Body Builder": {
                "Normal": "As a female bodybuilder considered obese, focus on high-intensity workouts that challenge your body and support fat loss. Incorporate activities such as high-intensity interval training (HIIT), circuit training, or sports activities for 45-60 minutes, 4-5 times a week. Work with a fitness professional to ensure proper form and technique.",
                "Expectant": "As a an expectant female body builder, focus on staying active with low-impact exercises that support overall fitness and well-being. Engage in activities such as swimming, prenatal yoga, or stationary cycling to maintain cardiovascular health and muscle strength. Listen to your body and consult with your healthcare provider for any modifications to your exercise routine during pregnancy.",
            },
            "Expectant": "Being expectant and considered obese, focus on maintaining a healthy lifestyle during pregnancy. While it's important to stay active, prioritize low-impact exercises that support your overall well-being and are safe for both you and your baby. Engage in activities such as walking, prenatal yoga, or swimming to maintain cardiovascular health and muscle strength without putting excessive strain on your body. Listen to your body and consult with your healthcare provider for personalized recommendations on exercise and nutrition during pregnancy."
        },
    }
}

def apply_theme(theme):
    root.configure(bg=theme["bg"])
    result_label.configure(bg=theme["bg"], fg=theme["fg"], font=("Arial", 12))
    calculate_button.configure(bg=theme["button_bg"], fg=theme["button_fg"], font=("Arial", 12))
    clear_button.configure(bg=theme["button_bg"], fg=theme["button_fg"], font=("Arial", 12))
    export_button.configure(bg=theme["button_bg"], fg=theme["button_fg"], font=("Arial", 12))

def apply_theme(theme):
    root.configure(bg=theme["bg"])
    result_label.configure(bg=theme["bg"], fg=theme["fg"], font=("Arial", 12))
    calculate_button.configure(bg=theme["button_bg"], fg=theme["button_fg"], font=("Arial", 12))
    clear_button.configure(bg=theme["button_bg"], fg=theme["button_fg"], font=("Arial", 12))
    export_button.configure(bg=theme["button_bg"], fg=theme["button_fg"], font=("Arial", 12))

def calculate_bmi(weight, height):
    """
    Calculate the Body Mass Index (BMI) using weight in kilograms and height in meters.
    Formula: BMI = weight (kg) / (height (m) ** 2)
    """
    if height == 0:
        messagebox.showerror("Error", "Height cannot be zero.")
        return None
    bmi = weight / (height ** 2)
    return bmi

def calculate_and_show_bmi():
    try:
        age = float(age_entry.get())
        weight = float(weight_entry.get())
        height = float(height_entry.get())

        bmi = calculate_bmi(weight, height)
        gender = gender_var.get()
        is_bodybuilder = bodybuilder_var.get()
        is_expectant = expectant_var.get()

        if bmi is not None:
            status, color, advice = interpret_bmi(weight, height, gender, is_bodybuilder, is_expectant)
            if status is not None:
                result_label.config(text=f"Status: {status}\nAdvice: {advice}", fg=color)
            else:
                messagebox.showerror("Error", "Failed to calculate BMI.")
        else:
            messagebox.showerror("Error", "Failed to calculate BMI.")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numerical values for age, weight, and height.")

def interpret_bmi(weight, height, gender, is_bodybuilder=False, is_expectant=False):
    bmi = calculate_bmi(weight, height)

    if bmi is not None:
        if bmi >= BMI_VALUES[-1]:  # Check if BMI is above or equal to 40
            bmi_category = "Obese"
        else:
            bmi_category = None
            for i, bmi_value in enumerate(BMI_VALUES):
                if bmi < bmi_value:
                    bmi_category = list(BMI_CATEGORIES.keys())[i]
                    break

        if bmi_category is not None:
            status = 'Normal'

            if gender == "Female":
                female_advice = DIET_ADVICE[bmi_category]["Female"]
                female_plan = EXERCISE_PLANS[bmi_category]["Female"]
                if is_bodybuilder and is_expectant:
                    advice = female_advice.get("Body Builder", {}).get("Expectant", female_advice["Normal"])
                    plan = female_plan.get("Body Builder", {}).get("Expectant", female_plan["Normal"])
                    status = 'BodyBuilder & Expectant'
                elif is_bodybuilder:
                    advice = female_advice.get("Body Builder", {}).get("Normal", female_advice["Normal"])
                    plan = female_plan.get("Body Builder", {}).get("Normal", female_plan["Normal"])
                    status = 'BodyBuilder'
                elif is_expectant:
                    advice = female_advice.get("Expectant", {})
                    plan = female_plan.get("Expectant", {})
                    status = 'Expectant'
                else:
                    advice = female_advice["Normal"]
                    plan = female_plan["Normal"]

            else:
                male_advice = DIET_ADVICE[bmi_category]["Male"]
                male_plan = EXERCISE_PLANS[bmi_category]["Male"]
                if is_bodybuilder:
                    advice = male_advice["Body Builder"]
                    plan = male_plan["Body Builder"]
                    status = 'BodyBuilder'
                else:
                    advice = male_advice["Normal"]
                    plan = male_plan["Normal"]

            return f"{bmi_category} ({gender} - {status})", BMI_CATEGORIES[bmi_category]["color"], advice, plan
        else:
            return "Category not found", "#000000", "No advice available", "No plan available"
    else:
        return None, None, None, None

def calculate_and_show_bmi():
    weight_str = weight_entry.get()
    height_str = height_entry.get()
    age_str = age_entry.get()

    if not validate_input(weight_str, height_str, age_str):
        return

    weight = float(weight_str)
    height = float(height_str)
    age = int(age_str)

    gender = gender_var.get()
    bmi = calculate_bmi(weight, height)
    is_expectant = expectant_var.get() == 1
    is_bodybuilder = bodybuilder_var.get() == 1
    status, color, advice, plan = interpret_bmi(weight, height, gender, is_bodybuilder=is_bodybuilder, is_expectant=is_expectant)

    result_label.config(
        text=f"Your BMI is: {bmi:.2f}\nYou are considered: {status}\nDiet advice: {advice}\nExercise Plan: {plan}", fg=color)

    # Plot BMI categories
    plot_bmi_categories(bmi)

def validate_input(weight_str, height_str, age_str):
    try:
        weight = float(weight_str)
        height = float(height_str)
        age = int(age_str)

        if weight <= 0 or weight > 635:
            raise ValueError("Weight must be a positive number less than or equal to 635.")

        if height <= 0 or height > 2.72:
            raise ValueError("Height must be a positive number less than or equal to 2.72.")

        if age <= 0 or age > 130:
            raise ValueError("Age must be a positive integer less than or equal to 130.")

        return True

    except ValueError as e:
        print(e)
        messagebox.showerror("Error", str(e))
        return False

def plot_bmi_categories(user_bmi):
    plt.figure(figsize=(8, 6))
    bars = plt.bar(list(BMI_CATEGORIES.keys()), BMI_VALUES, color=BMI_COLORS)

    # Plot user's BMI as a marker
    plt.plot([-0.5, len(list(BMI_CATEGORIES.keys())) - 0.5], [user_bmi,
             user_bmi], color='blue', linestyle='--', label='Your BMI')

    # Add labels to the bars indicating BMI ranges
    for i, bar in enumerate(bars):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, f"{BMI_VALUES[i]:.1f}", ha='center', va='bottom')

    # Highlight healthy BMI range
    plt.axhspan(BMI_VALUES[0], BMI_VALUES[1], color='green', alpha=0.1, label='Healthy Range')

    # Customize legend
    plt.legend()

    # Add titles and labels
    plt.xlabel('BMI Categories')
    plt.ylabel('BMI Value')
    plt.title('BMI Categories')
    plt.grid(True)

    # Show plot
    plt.tight_layout()
    plt.show()

def clear_entries():
    try:
        if messagebox.askokcancel("Confirmation", "Are you sure you want to clear all entries?"):
            weight_entry.delete(0, tk.END)
            height_entry.delete(0, tk.END)
            age_entry.delete(0, tk.END)
            name_entry.delete(0, tk.END)
            result_label.config(text="", fg="black")
    except Exception as e:
        # Handle the exception gracefully
        messagebox.showerror("Error", f"An error occurred: {e}")

def toggle_expectant_check(*args):
    if gender_var.get() == "Female":
        expectant_check.config(state="normal")
    else:
        expectant_check.config(state="disabled")
        expectant_var.set(0)

def change_theme(theme):
    if theme == "Default":
        apply_theme(DEFAULT_THEME)
    elif theme == "Alternate":
        apply_theme(ALTERNATE_THEME)

def export_report():
    try:
        name = name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter your name.")
            return

        weight = float(weight_entry.get())
        height = float(height_entry.get())
        age = int(age_entry.get())
        gender = gender_var.get()

        bmi = calculate_bmi(weight, height)
        is_expectant = expectant_var.get() == 1
        is_bodybuilder = bodybuilder_var.get() == 1
        status, color, advice, plan = interpret_bmi(
            weight, height, gender, is_bodybuilder=is_bodybuilder, is_expectant=is_expectant)

        # Choose export file format
        filetypes = [('PDF', '*.pdf'), ('CSV', '*.csv')]
        export_file = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=filetypes)

        if export_file:
            try:
                if export_file.endswith('.pdf'):
                    from fpdf import FPDF
    
                    # Define page size for landscape orientation (width, height)
                    pdf = FPDF(orientation='L', unit='mm', format='A4')
    
                    # Add a page
                    pdf.add_page()
    
                    # Set font
                    pdf.set_font("Arial", size=12)
    
                    # Define cell widths based on the landscape orientation
                    cell_width = pdf.w / 1.5
                    
                    # Add content to the PDF
                    pdf.cell(cell_width, 10, txt='BMI Report', ln=True, align='C')
                    pdf.cell(cell_width, 10, txt='', ln=True)  # Empty line for spacing
                    pdf.cell(cell_width, 10, txt=f'Name: {name}', ln=True)
                    pdf.cell(cell_width, 10, txt=f'Weight: {weight} kg', ln=True)
                    pdf.cell(cell_width, 10, txt=f'Height: {height} m', ln=True)
                    pdf.cell(cell_width, 10, txt=f'Age: {age}', ln=True)
                    pdf.cell(cell_width, 10, txt=f'Gender: {gender}', ln=True)
                    pdf.cell(cell_width, 10, txt=f'BMI: {bmi:.2f}', ln=True)
                    pdf.cell(cell_width, 10, txt=f'Weight Status: {status}', ln=True)
        
                    # Multicell for advice section
                    pdf.multi_cell(cell_width, 10, txt=f'Diet Advice: {advice}')
        
                    # Multicell for plan section
                    pdf.multi_cell(cell_width, 10, txt=f'Exercise Plan: {plan}')
        
                    # Save and show success message
                    pdf.output(export_file)
                    messagebox.showinfo("Success", f"Report exported successfully as {export_file}")

                elif export_file.endswith('.csv'):
                    with open(export_file, 'w', newline='') as csvfile:
                        fieldnames = ['Parameter', 'Value']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerow({'Parameter': 'Name', 'Value': name})
                        writer.writerow({'Parameter': 'Weight (kg)', 'Value': weight})
                        writer.writerow({'Parameter': 'Height (m)', 'Value': height})
                        writer.writerow({'Parameter': 'Age', 'Value': age})
                        writer.writerow({'Parameter': 'Gender', 'Value': gender})
                        writer.writerow({'Parameter': 'BMI', 'Value': bmi})
                        writer.writerow({'Parameter': 'Weight Status', 'Value': status})
                        writer.writerow(
                            {'Parameter': 'Diet Advice', 'Value': advice})
                        writer.writerow(
                            {'Parameter': 'Exercise Plan', 'Value': plan})
                    messagebox.showinfo("Success", f"Report exported successfully as {export_file}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while exporting the report: {str(e)}")
    except ValueError:
        messagebox.showerror("Error", "Invalid input. Please enter numerical values for weight, height, and age.")

# Create the main window
root = tk.Tk()
root.title("Personal Health Assistant")
window_width = 800
window_height = 800
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = int((screen_width / 2) - (window_width / 2))
y_coordinate = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

# Create labels
tk.Label(root, text="Name:", font=("Arial", 12)).place(relx=0.3, rely=0.05, anchor='center')
tk.Label(root, text="Mass (kg):", font=("Arial", 12)).place(relx=0.3, rely=0.1, anchor='center')
tk.Label(root, text="Height (m):", font=("Arial", 12)).place(relx=0.3, rely=0.15, anchor='center')
tk.Label(root, text="Age:", font=("Arial", 12)).place(relx=0.3, rely=0.2, anchor='center')
tk.Label(root, text="Gender:", font=("Arial", 12)).place(relx=0.3, rely=0.25, anchor='center')

# Create entry fields
name_entry = tk.Entry(root, font=("Arial", 12))
name_entry.place(relx=0.5, rely=0.05, anchor='center')
weight_entry = tk.Entry(root, font=("Arial", 12))
weight_entry.place(relx=0.5, rely=0.1, anchor='center')
height_entry = tk.Entry(root, font=("Arial", 12))
height_entry.place(relx=0.5, rely=0.15, anchor='center')
age_entry = tk.Entry(root, font=("Arial", 12))
age_entry.place(relx=0.5, rely=0.2, anchor='center')

# Gender dropdown menu
gender_var = tk.StringVar(root)
gender_var.set("Male")  # Default selection
gender_menu = tk.OptionMenu(root, gender_var, "Male", "Female", command=toggle_expectant_check)
gender_menu.place(relx=0.5, rely=0.25, anchor='center')

# Checkbox for expectant mothers
expectant_var = tk.IntVar()
expectant_check = tk.Checkbutton(root, text="Expectant Mother", variable=expectant_var, state="disabled")
expectant_check.place(relx=0.5, rely=0.3, anchor='center')

# Checkbox for bodybuilders
bodybuilder_var = tk.IntVar()
bodybuilder_check = tk.Checkbutton(root, text="Bodybuilder", variable=bodybuilder_var)
bodybuilder_check.place(relx=0.5, rely=0.35, anchor='center')

# Create the calculate, clear, and export buttons
calculate_button = tk.Button(root, text="Calculate BMI", command=calculate_and_show_bmi, font=("Arial", 12))
calculate_button.place(relx=0.3, rely=0.4, anchor='center')
clear_button = tk.Button(root, text="Clear", command=clear_entries, font=("Arial", 12))
clear_button.place(relx=0.5, rely=0.4, anchor='center')
export_button = tk.Button(root, text="Export Report", command=export_report, font=("Arial", 12))
export_button.place(relx=0.7, rely=0.4, anchor='center')

# Result label
result_label = tk.Label(root, text="", wraplength=400)
result_label.place(relx=0.5, rely=0.7, anchor='center')

# Create a dropdown menu for changing theme
theme_var = tk.StringVar(root)
theme_var.set("Default")  # Default theme selected
theme_menu = tk.OptionMenu(root, theme_var, "Default", "Alternate", command=change_theme)
theme_menu.place(relx=0.5, rely=0.01, anchor='center')

# Apply default theme initially
apply_theme(DEFAULT_THEME)

# Run the main event loop
root.mainloop()
