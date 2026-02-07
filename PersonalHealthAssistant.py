import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog, ttk
import csv
import json
import os
import sys
import shutil
from datetime import datetime
import unicodedata
import tempfile

# Lazy matplotlib imports to improve startup time
_MPL_READY = False
plt = None
Figure = None
FigureCanvasTkAgg = None
NavigationToolbar2Tk = None
mdates = None

def ensure_matplotlib():
    global _MPL_READY, plt, Figure, FigureCanvasTkAgg, NavigationToolbar2Tk, mdates
    if _MPL_READY:
        return True
    try:
        import matplotlib
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as _plt
        from matplotlib.figure import Figure as _Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as _FigureCanvasTkAgg
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as _NavigationToolbar2Tk
        import matplotlib.dates as _mdates

        _plt.ioff()
        plt = _plt
        Figure = _Figure
        FigureCanvasTkAgg = _FigureCanvasTkAgg
        NavigationToolbar2Tk = _NavigationToolbar2Tk
        mdates = _mdates
        _MPL_READY = True
        return True
    except Exception as e:
        messagebox.showerror('Error', f'Failed to load plotting libraries: {e}')
        return False

# Define default colors and themes (kept for compatibility)
DEFAULT_THEME = {
    "bg": "white",
    "fg": "black",
    "button_bg": "#4CAF50",
    "button_fg": "white",
}

ALTERNATE_THEME = {
    "bg": "#263238",
    "fg": "white",
    "button_bg": "#FF5722",
    "button_fg": "white",
}

# Try to use ttkbootstrap for a modern look, fallback to standard ttk
try:
    import ttkbootstrap as tb
    from ttkbootstrap.constants import *
    _style = tb.Style("flatly")
    USE_TTB = True
except Exception:
    _style = None
    USE_TTB = False

def apply_theme(theme):
    # Accept either a theme dict or a theme name string.
    if isinstance(theme, str):
        if theme == 'Default':
            theme = {
                "bg": "white",
                "fg": "black",
                "button_bg": "#4CAF50",
                "button_fg": "white",
            }
        elif theme == 'Alternate':
            theme = {
                "bg": "#263238",
                "fg": "white",
                "button_bg": "#FF5722",
                "button_fg": "white",
            }
        else:
            theme = globals().get(theme, {
                "bg": "white",
                "fg": "black",
                "button_bg": "#4CAF50",
                "button_fg": "white",
            })
    # Defensive: ensure theme is a mapping with .get
    if not hasattr(theme, 'get'):
        theme = {
            "bg": "white",
            "fg": "black",
            "button_bg": "#4CAF50",
            "button_fg": "white",
        }

    # Apply theme colors across ttk styles and key widgets.
    bg = theme.get("bg", "white")
    fg = theme.get("fg", "black")
    button_bg = theme.get("button_bg", "#4CAF50")
    button_fg = theme.get("button_fg", "white")
    try:
        root.configure(bg=bg)
    except Exception:
        pass

    try:
        # Configure common ttk styles
        style.configure('TFrame', background=bg)
        style.configure('TLabel', background=bg, foreground=fg)
        style.configure('TEntry', fieldbackground='#FFFFFF', foreground=fg)
        style.configure('TButton', background=button_bg, foreground=button_fg)
        style.configure('Card.TLabelframe', background=bg)
        style.configure('Card.TLabelframe.Label', background=bg, foreground=fg)
        # Treeview
        style.configure('Treeview', background='#FFFFFF', fieldbackground='#FFFFFF', foreground=fg)
        style.map('TButton', background=[('active', button_bg)])
    except Exception:
        pass

    # Try to update specific widgets' colors for immediate visual feedback
    try:
        for name in ('main_frame', 'left_frame', 'right_frame', 'bottom_frame', 'results_frame', 'plot_frame'):
            if name in globals():
                w = globals()[name]
                try:
                    w.configure(style='TFrame')
                except Exception:
                    try:
                        w.config(background=bg)
                    except Exception:
                        pass
    except Exception:
        pass

    try:
        result_label.config(background=bg, foreground=fg)
    except Exception:
        try:
            result_label.config(foreground=fg)
        except Exception:
            pass

    try:
        profiles_tree.configure(background='#FFFFFF', foreground=fg)
    except Exception:
        pass

    # If ttkbootstrap is available, try to set a compatible bootstyle for buttons
    if USE_TTB:
        try:
            # prefer 'primary' for default, 'warning' for alternate if colors differ
            boot = 'primary'
            if button_bg and button_bg.startswith('#FF'):
                boot = 'warning'
            # apply bootstyle to buttons if they were created via tb.Button
            for child in root.winfo_children():
                try:
                    if isinstance(child, tb.Button):
                        child.config(bootstyle=boot)
                except Exception:
                    pass
        except Exception:
            pass

# Profiles persistence - handle bundled exe case
try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = sys._MEIPASS
    BUNDLED = True
except AttributeError:
    base_path = os.path.dirname(__file__)
    BUNDLED = False

if BUNDLED:
    # For bundled exe, store profiles in user's app data directory
    app_data_dir = os.path.join(os.path.expanduser("~"), "PersonalHealthAssistant")
    os.makedirs(app_data_dir, exist_ok=True)
    PROFILES_FILE = os.path.join(app_data_dir, 'profiles.json')
else:
    # For development, use local file
    PROFILES_FILE = os.path.join(base_path, 'profiles.json')

def load_profiles_file():
    try:
        # If bundled and profiles file doesn't exist in user directory, copy from bundle
        if BUNDLED and not os.path.exists(PROFILES_FILE):
            bundled_profiles = os.path.join(base_path, 'profiles.json')
            if os.path.exists(bundled_profiles):
                shutil.copy2(bundled_profiles, PROFILES_FILE)

        if os.path.exists(PROFILES_FILE):
            with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_profiles_file(profiles):
    try:
        with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=2)
        return True
    except Exception as e:
        messagebox.showerror('Error', f'Failed to save profiles: {e}')
        return False

def update_profiles_view():
    try:
        profiles = load_profiles_file()
        profiles_tree.delete(*profiles_tree.get_children())
        for name, data in profiles.items():
            age = data.get('age', '')
            gender = data.get('gender', '')
            ts = data.get('saved_at', '')
            profiles_tree.insert('', 'end', iid=name, values=(name, age, gender, ts))
    except Exception:
        pass

def save_profile():
    name = name_entry.get().strip()
    if not name:
        messagebox.showerror('Error', 'Please enter a name to save the profile.')
        return
    try:
        profiles = load_profiles_file()
        existing = profiles.get(name, {})
        profile = {
            'name': name,
            'weight': weight_entry.get().strip(),
            'height': height_entry.get().strip(),
            'age': age_entry.get().strip(),
            'gender': gender_var.get(),
            'bodybuilder': int(bodybuilder_var.get()),
            'expectant': int(expectant_var.get()),
            'history': existing.get('history', []),
            'goal': existing.get('goal', {}),
            'saved_at': datetime.utcnow().isoformat()
        }
        profiles[name] = profile
        if save_profiles_file(profiles):
            update_profiles_view()
            messagebox.showinfo('Saved', f'Profile "{name}" saved.')
    except Exception as e:
        messagebox.showerror('Error', f'Failed to save profile: {e}')

def load_selected_profile(event=None):
    sel = profiles_tree.focus()
    if not sel:
        selection = profiles_tree.selection()
        if not selection:
            messagebox.showerror('Error', 'No profile selected.')
            return
        sel = selection[0]
    profiles = load_profiles_file()
    profile = profiles.get(sel)
    if not profile:
        messagebox.showerror('Error', 'Selected profile not found.')
        return
    try:
        name_entry.delete(0, tk.END)
        name_entry.insert(0, profile.get('name', ''))
        weight_entry.delete(0, tk.END)
        weight_entry.insert(0, profile.get('weight', ''))
        height_entry.delete(0, tk.END)
        height_entry.insert(0, profile.get('height', ''))
        age_entry.delete(0, tk.END)
        age_entry.insert(0, profile.get('age', ''))
        gender_var.set(profile.get('gender', 'Male'))
        bodybuilder_var.set(profile.get('bodybuilder', 0))
        expectant_var.set(profile.get('expectant', 0))
        toggle_expectant_check()
        try:
            goal_bmi_entry.delete(0, tk.END)
            goal_bmi = profile.get('goal', {}).get('bmi', '')
            if goal_bmi != '':
                goal_bmi_entry.insert(0, str(goal_bmi))
        except Exception:
            pass
        messagebox.showinfo('Loaded', f'Profile "{profile.get("name")}" loaded.')
    except Exception as e:
        messagebox.showerror('Error', f'Failed to load profile: {e}')

def delete_profile():
    sel = profiles_tree.focus()
    if not sel:
        selection = profiles_tree.selection()
        if not selection:
            messagebox.showerror('Error', 'No profile selected to delete.')
            return
        sel = selection[0]
    if not messagebox.askyesno('Confirm', f'Delete profile "{sel}"?'):
        return
    profiles = load_profiles_file()
    if sel in profiles:
        profiles.pop(sel)
        save_profiles_file(profiles)
        update_profiles_view()
        messagebox.showinfo('Deleted', f'Profile "{sel}" deleted.')

DIET_ADVICE = {
    "Underweight": {
        "Male": {
            "Normal": "Focus on nourishing your body with nutrient-rich foods that can help you gain healthy weight. Consider increasing your calorie intake by incorporating foods such as groundnuts, sunflower seeds, avocados, ugali (maize meal), brown rice, lean proteins like chicken, tilapia fish, goat meat, beans, and lentils into your diet. Additionally, prioritize regular meals and snacks throughout the day to support weight gain. Include local fruits like mangoes, bananas, and oranges for natural sweetness and nutrients. Consult with a local healthcare provider or nutritionist in Kenya for personalized advice.",
            "Body Builder": "As a male bodybuilder who is underweight, focus on increasing your calorie intake with nutrient-dense foods to support muscle growth. Include a balance of protein, carbohydrates, and healthy fats in your meals. Consider incorporating foods such as lean meats like chicken or goat, eggs, dairy like milk and yogurt, ugali, brown rice, fruits like bananas and mangoes, and vegetables like sukuma wiki and tomatoes. Additionally, prioritize strength training exercises to build muscle mass. Consult with a local healthcare provider or nutritionist in Kenya for personalized advice."
        },
        "Female": {
            "Normal": "Focus on nourishing your body with nutrient-rich foods that can help you gain healthy weight. Consider increasing your calorie intake by incorporating foods such as groundnuts, sunflower seeds, avocados, ugali (maize meal), brown rice, lean proteins like chicken, tilapia fish, goat meat, beans, and lentils into your diet. Additionally, prioritize regular meals and snacks throughout the day to support weight gain. Include local fruits like mangoes, bananas, and oranges for natural sweetness and nutrients. Consult with a local healthcare provider or nutritionist in Kenya for personalized advice.",
            "Body Builder": {
                "Normal": "As a female bodybuilder who is underweight, focus on increasing your calorie intake with nutrient-dense foods to support muscle growth. Include a balance of protein, carbohydrates, and healthy fats in your meals. Consider incorporating foods such as lean meats like chicken or goat, eggs, dairy like milk and yogurt, ugali, brown rice, fruits like bananas and mangoes, and vegetables like sukuma wiki and tomatoes. Additionally, prioritize strength training exercises to build muscle mass. Consult with a local healthcare provider or nutritionist in Kenya for personalized advice.",
                "Expectant": "As you prepare for motherhood, prioritize your health and your baby's well-being. If you're into bodybuilding, focus on nourishing foods like groundnuts, lean proteins like chicken and fish, avocados, dairy like milk and yogurt, ugali and whole grains. Stay energized with regular meals and snacks. And remember, consulting your healthcare provider can offer tailored advice for a healthy pregnancy journey. In Kenya, include folate-rich foods like sukuma wiki and beans.",
            },
            "Expectant": "As an expectant female, it's important to focus on gaining weight in a healthy manner to support both your own health and the health of your baby. Incorporate nutrient-dense foods such as groundnuts, sunflower seeds, avocados, lean proteins like chicken, tilapia, goat meat, ugali, brown rice, and dairy like milk and yogurt into your diet. Aim to eat regular meals and snacks to ensure you're meeting your increased calorie needs during pregnancy. Include local fruits like mangoes and bananas. Consult with a healthcare provider or dietitian for personalized guidance, preferably one familiar with Kenyan dietary practices."
        }
    },
    "Normal weight": {
        "Male": {
            "Normal": "Maintaining a balanced diet is key to sustaining your current healthy weight. Ensure you're consuming a variety of fruits like mangoes, bananas, oranges, vegetables like sukuma wiki, tomatoes, onions, ugali (maize meal), brown rice, and lean proteins such as chicken, tilapia fish, goat meat, beans, and lentils. Aim for a balanced plate at each meal, focusing on portion control and including foods from all food groups. Remember to stay hydrated by drinking plenty of water throughout the day. In Kenya, enjoy local dishes like chapati in moderation. Consult with a local healthcare provider for personalized advice.",
            "Body Builder": "As a male bodybuilder with a normal weight, focus on maintaining your current weight while supporting muscle growth and performance. Consume a balanced diet that includes a mix of lean proteins like chicken, goat meat, eggs, complex carbohydrates like ugali and brown rice, healthy fats from avocados and groundnuts, fruits like bananas and mangoes, and vegetables like sukuma wiki and spinach. Consider timing your meals around your workouts to optimize energy levels and recovery. Consult with a local healthcare provider or nutritionist in Kenya for personalized advice.",
        },
        "Female": {
            "Normal": "Maintaining a balanced diet is key to sustaining your current healthy weight. Ensure you're consuming a variety of fruits like mangoes, bananas, oranges, vegetables like sukuma wiki, tomatoes, onions, ugali (maize meal), brown rice, and lean proteins such as chicken, tilapia fish, goat meat, beans, and lentils. Aim for a balanced plate at each meal, focusing on portion control and including foods from all food groups. Remember to stay hydrated by drinking plenty of water throughout the day. In Kenya, enjoy local dishes like chapati in moderation. Consult with a local healthcare provider for personalized advice.",
            "Body Builder": {
                "Normal": "As a female bodybuilder with a normal weight, focus on maintaining your current weight while supporting muscle growth and performance. Consume a balanced diet that includes a mix of lean proteins like chicken, goat meat, eggs, complex carbohydrates like ugali and brown rice, healthy fats from avocados and groundnuts, fruits like bananas and mangoes, and vegetables like sukuma wiki and spinach. Consider timing your meals around your workouts to optimize energy levels and recovery. Consult with a local healthcare provider or nutritionist in Kenya for personalized advice.",
                "Expectant": "As a bodybuilder with a normal weight who is expecting, continue to prioritize a balanced diet that supports both your health and the health of your baby. Ensure you're consuming a variety of nutrient-dense foods including fruits like mangoes and bananas, vegetables like sukuma wiki and tomatoes, ugali, brown rice, lean proteins like chicken and fish, and healthy fats from avocados. Stay hydrated and consult with your healthcare provider for personalized nutrition recommendations during pregnancy, preferably one familiar with Kenyan diets.",
            },
            "Expectant": "As an expectant female with a normal weight, prioritize a diet rich in nutrients crucial for pregnancy, such as folate, calcium, iron, and omega-3 fatty acids. Include foods like leafy greens such as sukuma wiki, dairy products like milk and yogurt, lean meats like chicken, fish like tilapia, groundnuts, and sunflower seeds. Aim for regular, balanced meals and snacks to provide steady energy throughout the day. Consult with your healthcare provider for personalized dietary recommendations to support a healthy pregnancy, considering local Kenyan foods."
        }
    },
    "Overweight": {
        "Male": {
            "Normal": "It is important to focus on making gradual, sustainable changes to your diet and lifestyle. Start by incorporating more whole, nutrient-dense foods like fruits such as mangoes and bananas, vegetables like sukuma wiki, tomatoes, onions, lean proteins like chicken, tilapia fish, goat meat, and ugali (maize meal) or brown rice into your meals. Practice portion control and limit your intake of processed foods, sugary snacks like mandazi, and high-calorie beverages like soda. In Kenya, reduce consumption of fried foods and opt for grilled or boiled options. Consult with a local healthcare provider or nutritionist for personalized advice.",
            "Body Builder": "As a male bodybuilder who is overweight, focus on creating a calorie deficit through a combination of diet and exercise to support fat loss while maintaining muscle mass. Incorporate plenty of lean proteins like chicken, goat meat, eggs, fruits like bananas and oranges, vegetables like sukuma wiki and spinach, and ugali or brown rice into your meals while reducing your intake of high-calorie foods and sugary snacks. Prioritize strength training to preserve muscle mass during weight loss. Consult with a local healthcare provider or nutritionist in Kenya for personalized advice."
        },
        "Female": {
            "Normal": "It is important to focus on making gradual, sustainable changes to your diet and lifestyle. Start by incorporating more whole, nutrient-dense foods like fruits such as mangoes and bananas, vegetables like sukuma wiki, tomatoes, onions, lean proteins like chicken, tilapia fish, goat meat, and ugali (maize meal) or brown rice into your meals. Practice portion control and limit your intake of processed foods, sugary snacks like mandazi, and high-calorie beverages like soda. In Kenya, reduce consumption of fried foods and opt for grilled or boiled options. Consult with a local healthcare provider or nutritionist for personalized advice.",
            "Body Builder": {
                "Normal": "As a female bodybuilder who is overweight, focus on creating a calorie deficit through a combination of diet and exercise to support fat loss while maintaining muscle mass. Incorporate plenty of lean proteins like chicken, goat meat, eggs, fruits like bananas and oranges, vegetables like sukuma wiki and spinach, and ugali or brown rice into your meals while reducing your intake of high-calorie foods and sugary snacks. Prioritize strength training to preserve muscle mass during weight loss. Consult with a local healthcare provider or nutritionist in Kenya for personalized advice.",
                "Expectant": "As a bodybuilder who is overweight and expecting, it's important to focus on gaining weight in a healthy manner to support both your own health and the health of your baby. Aim to make gradual, sustainable changes to your diet by incorporating more whole, nutrient-dense foods like fruits, vegetables, lean proteins, and ugali while reducing your intake of processed foods, sugary snacks, and high-calorie beverages. Consult with a healthcare provider or dietitian for personalized guidance, preferably one familiar with Kenyan dietary practices.",
            },
            "Expectant": "As an expectant female who is overweight, it is important to focus on making gradual, sustainable changes to your diet and lifestyle to support both your health and the health of your baby. Incorporate more whole, nutrient-dense foods like fruits such as mangoes, vegetables like sukuma wiki, lean proteins like chicken and fish, and ugali into your meals. Practice portion control and limit your intake of processed foods, sugary snacks, and high-calorie beverages. Consult with a healthcare provider or dietitian for personalized guidance during pregnancy, considering local Kenyan foods."
        }
    },
    "Obese": {
        "Male": {
            "Normal": "As an obese male seeking to improve health, focus on a balanced diet rich in fruits like mangoes and bananas, vegetables like sukuma wiki and tomatoes, lean proteins like chicken, tilapia fish, goat meat, and ugali (maize meal) or brown rice while reducing intake of high-calorie processed foods like fried snacks. Emphasize portion control and consider meal planning to support weight loss goals. In Kenya, limit sugary drinks and opt for water or herbal teas. Consult with a local healthcare provider or nutritionist for personalized advice.",
            "Body Builder": "As a male bodybuilder who is obese, prioritize seeking support from healthcare professionals or registered dietitians who can provide personalized guidance and support. Together, you can develop a comprehensive meal plan tailored to your specific dietary needs and weight loss goals. Focus on incorporating plenty of fruits like bananas, vegetables like sukuma wiki, lean proteins like chicken and goat meat, and ugali or brown rice into your diet while reducing your intake of high-calorie, processed foods. Consult with a local healthcare provider or nutritionist in Kenya for personalized advice.",
        },
        "Female": {
            "Normal": "As an obese female focused on health improvement, emphasize a balanced diet with plenty of fruits like mangoes and bananas, vegetables like sukuma wiki and tomatoes, lean proteins like chicken, tilapia fish, goat meat, and ugali (maize meal) or brown rice while minimizing high-calorie processed foods. Practice portion control and consider meal planning to support weight loss efforts. In Kenya, limit sugary drinks and opt for water or herbal teas. Consult with a local healthcare provider or nutritionist for personalized advice.",
            "Body Builder": {
                "Normal": "As a female bodybuilder who is obese, prioritize seeking support from healthcare professionals or registered dietitians who can provide personalized guidance and support. Together, you can develop a comprehensive meal plan tailored to your specific dietary needs and weight loss goals. Focus on incorporating plenty of fruits like bananas, vegetables like sukuma wiki, lean proteins like chicken and goat meat, and ugali or brown rice into your diet while reducing your intake of high-calorie, processed foods. Consult with a local healthcare provider or nutritionist in Kenya for personalized advice.",
                "Expectant": "As a bodybuilder who is obese and expecting, it's important to focus on gaining weight in a healthy manner to support both your own health and the health of your baby. Seek support from healthcare professionals or registered dietitians who can provide personalized guidance and support. Together, you can develop a comprehensive meal plan tailored to your specific dietary needs and weight loss goals. Focus on incorporating plenty of fruits like mangoes, vegetables like sukuma wiki, lean proteins like chicken and fish, and ugali into your diet while reducing your intake of high-calorie, processed foods. Consult with a healthcare provider familiar with Kenyan diets.",
            },
            "Expectant": "As an expectant female considered obese, it is important to focus on a balanced diet that supports both your health and the health of your baby. Aim to consume a variety of nutrient-dense foods including fruits like mangoes and bananas, vegetables like sukuma wiki and tomatoes, lean proteins like chicken and tilapia, ugali or brown rice, and healthy fats from avocados. Practice portion control and limit your intake of processed foods, sugary snacks, and high-calorie beverages. Ensure you stay hydrated by drinking plenty of water throughout the day. While it's beneficial to consult with healthcare professionals, focusing on a healthy diet can be a positive step in managing weight during pregnancy. Seek advice from a local Kenyan healthcare provider."
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

# `apply_theme` handled earlier with ttkbootstrap fallback; GUI styling
# should be managed by ttk/ttkbootstrap style objects where available.

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

# Note: older, simpler `calculate_and_show_bmi` removed to avoid duplicate definitions.

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


def generate_personalized_advice(bmi_category, gender, age, is_bodybuilder, is_expectant, diet_pref, base_advice, base_plan):
    """Create expanded, AI-like advice text using profile and base advice/plan.

    This is a deterministic template-based generator (no external AI required).
    """
    lines = []
    lines.append(f"Summary: You are classified as {bmi_category}. {base_advice}")

    # Tone and focus
    focus = "muscle-building and higher protein" if is_bodybuilder else "balanced health and gradual change"
    if is_expectant:
        focus = "supporting pregnancy nutrition and gentle activity"

    lines.append(f"Focus: {focus}. Recommended approach: small, sustainable steps with consistent tracking.")

    # Diet-specific suggestions
    if diet_pref == 'Vegetarian':
        protein_sources = 'beans, lentils, groundnuts, tofu, tempeh, Greek yogurt, cottage cheese, eggs (if used)'
    elif diet_pref == 'Vegan':
        protein_sources = 'lentils, chickpeas, groundnuts, tofu, tempeh, seitan, soy-based products, nuts and seeds'
    elif diet_pref == 'Pescatarian':
        protein_sources = 'tilapia, Nile perch, eggs, dairy, beans and ugali'
    elif diet_pref == 'Keto':
        protein_sources = 'fatty fish like tilapia, meats like goat, eggs, high-fat dairy, groundnuts and sunflower seeds, low-carb vegetables like sukuma wiki'
    elif diet_pref == 'Low-Carb':
        protein_sources = 'lean meats like chicken, goat, tilapia, eggs, sukuma wiki, groundnuts and sunflower seeds'
    else:
        protein_sources = 'lean meats like chicken, goat, tilapia, eggs, dairy, beans, and groundnuts'

    lines.append(f"Good protein and nutrient sources for a {diet_pref.lower()} approach: {protein_sources}.")

    # Sample day depending on BMI category
    if bmi_category in ('Underweight',):
        lines.append("Sample day: Breakfast — ugali with groundnut butter, banana, and milk; Snack — yogurt + mixed nuts; Lunch — rice salad with beans; Snack — smoothie with protein powder; Dinner — tilapia or lentils with sweet potato and sukuma wiki.")
    elif bmi_category in ('Normal weight',):
        lines.append("Sample day: Breakfast — eggs/avocado on chapati; Snack — fruit + nuts; Lunch — grilled chicken or bean stew with brown rice; Snack — hummus + veggies; Dinner — fish/legume stew and sukuma wiki salad.")
    else:
        lines.append("Sample day: Breakfast — Greek yogurt with mangoes and sunflower seeds; Snack — raw veggies like tomatoes and hummus; Lunch — large sukuma wiki salad with lean protein like chicken; Snack — orange + groundnut butter; Dinner — grilled tilapia/lean goat meat and steamed vegetables.")

    # Practical tips
    tips = [
        "Aim for 3 balanced meals and 1–2 nutrient-dense snacks per day.",
        "Include one source of protein with each meal to support satiety and muscle maintenance.",
        "Prefer whole foods over processed options; read labels for added sugars and sodium.",
        "Stay hydrated — water before meals can help with appetite regulation.",
    ]
    if is_bodybuilder:
        tips.append("Consider timing carbohydrate intake around workouts and prioritize post-workout protein for recovery.")
    if is_expectant:
        tips.append("Ensure adequate folate, iron and calcium; consult your healthcare provider for prenatal vitamins.")

    lines.append("Practical tips: " + ' '.join(tips))

    # Weekly micro-plan (3 bullet points)
    lines.append("Weekly micro-plan: 1) Plan 3 dinners that include a lean protein + 2 vegetables; 2) Prep 2 portable snacks (nuts, yogurt, hummus+veggies); 3) Schedule 3 short strength or brisk-walk sessions.")

    # Safety / personalization note
    lines.append("Note: These suggestions are general. For medical conditions, pregnancy concerns, or special dietary needs, consult a healthcare professional or registered dietitian.")

    return '\n\n'.join(lines)

def calculate_and_show_bmi():
    try:
        weight_str = weight_entry.get()
        height_str = height_entry.get()
        age_str = age_entry.get()

        if not validate_input(weight_str, height_str, age_str):
            return

        weight = float(weight_str)
        height = float(height_str)
        age = int(age_str)

        gender = gender_var.get()
        is_expectant = expectant_var.get() == 1
        is_bodybuilder = bodybuilder_var.get() == 1
        bmi = calculate_bmi(weight, height)
        status, color, advice, plan = interpret_bmi(weight, height, gender, is_bodybuilder=is_bodybuilder, is_expectant=is_expectant)

        # Record data for tracking
        name = name_entry.get().strip()
        if name:
            try:
                profiles = load_profiles_file()
                if name not in profiles:
                    profiles[name] = {'history': []}
                entry = {
                    'date': datetime.utcnow().isoformat(),
                    'weight': weight,
                    'height': height,
                    'bmi': bmi,
                    'category': status.split(' ')[0],
                    'gender': gender,
                    'age': age,
                    'bodybuilder': is_bodybuilder,
                    'expectant': is_expectant
                }
                profiles[name]['history'].append(entry)
                save_profiles_file(profiles)
            except Exception:
                pass  # Silently fail for history recording

        # Generate expanded AI-like suggestions using diet preference and profile
        diet_pref = 'Omnivore'

        detailed = generate_personalized_advice(status.split(' ')[0], gender, age, is_bodybuilder, is_expectant, diet_pref, advice, plan)

        # Analyze trend for encouragement/warning
        trend_message = ""
        goal_message = ""
        if name:
            try:
                profiles = load_profiles_file()
                profile = profiles.get(name, {})
                history = profile.get('history', [])
                goal = profile.get('goal', {})
                
                # Trend analysis
                if len(history) >= 2:
                    last_entry = history[-1]
                    prev_entry = history[-2]
                    last_bmi = last_entry['bmi']
                    prev_bmi = prev_entry['bmi']
                    last_weight = last_entry['weight']
                    prev_weight = prev_entry['weight']
                    category = status.split(' ')[0]
                    bmi_delta = last_bmi - prev_bmi
                    weight_delta = last_weight - prev_weight
                    
                    bmi_trend = ""
                    if last_bmi < prev_bmi:
                        bmi_trend = f"🎉 BMI decreased by {prev_bmi - last_bmi:.2f} points"
                    elif last_bmi > prev_bmi:
                        bmi_trend = f"⚠️ BMI increased by {last_bmi - prev_bmi:.2f} points"
                    else:
                        bmi_trend = "BMI is stable"
                    
                    weight_trend = ""
                    if last_weight < prev_weight:
                        weight_trend = f" (Weight down {prev_weight - last_weight:.1f} kg)"
                    elif last_weight > prev_weight:
                        weight_trend = f" (Weight up {last_weight - prev_weight:.1f} kg)"
                    else:
                        weight_trend = " (Weight stable)"
                    
                    trend_message = f"{bmi_trend}{weight_trend}. "

                    # Tailor guidance by BMI category and recent changes
                    drastic_weight_change = abs(weight_delta) >= 2.0
                    drastic_bmi_change = abs(bmi_delta) >= 1.0

                    if category == "Underweight":
                        if weight_delta > 0 or bmi_delta > 0:
                            trend_message += "Great progress. Keep working toward gradual weight gain."
                        elif weight_delta < 0 or bmi_delta < 0:
                            trend_message += "Focus on increasing weight with nutrient-dense meals."
                        else:
                            trend_message += "Aim for a slow, steady weight increase."
                    elif category in ("Overweight", "Obese"):
                        if weight_delta < 0 or bmi_delta < 0:
                            trend_message += "Good direction. Keep focusing on gradual weight loss."
                        elif weight_delta > 0 or bmi_delta > 0:
                            trend_message += "Focus on healthy weight reduction habits."
                        else:
                            trend_message += "Consider a gradual weight-loss plan."
                    else:
                        if drastic_weight_change or drastic_bmi_change:
                            trend_message += "Warning: large recent changes. Try to keep weight changes gradual and steady."
                        elif weight_delta != 0 or bmi_delta != 0:
                            trend_message += "Small changes are normal. Keep monitoring your trend."
                        else:
                            trend_message += "Maintain your current routine."
                    
                    # Long-term trend
                    if len(history) >= 3:
                        first_bmi = history[0]['bmi']
                        if last_bmi < first_bmi:
                            trend_message += f" Overall, strong downward trend since first calculation ({first_bmi - last_bmi:.2f} points lower)."
                        elif last_bmi > first_bmi:
                            trend_message += f" Overall, upward trend since first calculation ({last_bmi - first_bmi:.2f} points higher)."
                        else:
                            trend_message += " Overall trend is stable."
                
                # Goal progress
                if goal:
                    current_bmi = bmi
                    goal_bmi = goal.get('bmi')

                    if goal_bmi:
                        diff_bmi = goal_bmi - current_bmi
                        if abs(diff_bmi) < 0.1:
                            goal_message += "BMI goal achieved!"
                        elif diff_bmi > 0:
                            goal_message += f"{diff_bmi:.2f} BMI points to goal."
                        else:
                            goal_message += f"{abs(diff_bmi):.2f} BMI points over goal."

                    if goal_message:
                        goal_message = "Goal Progress: " + goal_message
                
            except:
                pass

        if trend_message:
            detailed += "\n\n" + trend_message
        if goal_message:
            detailed += "\n\n" + goal_message

        # If a named profile has a goal, append a goal-achievement micro-plan
        try:
            name = name_entry.get().strip()
            profiles = load_profiles_file()
            if name and name in profiles and profiles[name].get('goal'):
                goal_plan = generate_goal_plan(name)
                if goal_plan:
                    detailed = detailed + "\n\nGOAL PLAN:\n" + goal_plan
        except Exception:
            pass

        # store last detailed advice for viewer
        global last_advice_text
        last_advice_text = detailed

        # Show a concise summary in the results label, detailed view available via button
        summary = f"Your BMI is: {bmi:.2f}\nYou are considered: {status}\nTap 'Detailed Advice' for meal ideas and tips."
        if trend_message:
            summary += "\n\n" + trend_message
        result_label.config(text=summary, foreground=color)

        # Plot BMI categories
        plot_bmi_categories(bmi)

        # Record reading into profile history when a name is provided.
        try:
            name = name_entry.get().strip()
            if name:
                add_history_entry(
                    name,
                    weight,
                    height,
                    bmi,
                    age=age,
                    gender=gender,
                    bodybuilder=is_bodybuilder,
                    expectant=is_expectant
                )
        except Exception:
            pass
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def validate_input(weight_str, height_str, age_str):
    weight_str = weight_str.strip()
    height_str = height_str.strip()
    age_str = age_str.strip()

    if not weight_str or not height_str or not age_str:
        messagebox.showerror("Error", "Please enter weight, height, and age.")
        return False

    try:
        weight = float(weight_str)
    except ValueError:
        messagebox.showerror("Error", "Weight must be a number.")
        return False

    try:
        height = float(height_str)
    except ValueError:
        messagebox.showerror("Error", "Height must be a number.")
        return False

    try:
        age = int(age_str)
    except ValueError:
        messagebox.showerror("Error", "Age must be a whole number.")
        return False

    if weight <= 0 or weight > 635:
        messagebox.showerror("Error", "Weight must be a positive number less than or equal to 635.")
        return False

    if height <= 0 or height > 2.72:
        messagebox.showerror("Error", "Height must be a positive number less than or equal to 2.72.")
        return False

    if age <= 0 or age > 130:
        messagebox.showerror("Error", "Age must be a positive integer less than or equal to 130.")
        return False

    return True

def plot_bmi_categories(user_bmi):
    if not ensure_matplotlib():
        return
    # Create a Figure and draw onto it, then embed into the GUI
    try:
        plt.close('all')
    except Exception:
        pass

    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)
    bars = ax.bar(list(BMI_CATEGORIES.keys()), BMI_VALUES, color=BMI_COLORS)

    # Plot user's BMI as a horizontal marker line
    ax.plot([-0.5, len(list(BMI_CATEGORIES.keys())) - 0.5], [user_bmi, user_bmi], color='blue', linestyle='--', label='Your BMI')

    for i, bar in enumerate(bars):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, f"{BMI_VALUES[i]:.1f}", ha='center', va='bottom')

    ax.axhspan(BMI_VALUES[0], BMI_VALUES[1], color='green', alpha=0.1, label='Healthy Range')
    ax.set_xlabel('BMI Categories')
    ax.set_ylabel('BMI Value')
    ax.set_title('BMI Categories')
    ax.grid(True)
    ax.legend()

    # Embed in Tkinter: destroy previous canvas if present
    global plot_canvas, plot_frame
    try:
        if plot_canvas:
            plot_canvas.get_tk_widget().destroy()
    except Exception:
        pass
    # Ensure plot_frame (created in layout) exists; otherwise create inside bottom_frame
    try:
        if plot_frame is None:
            plot_frame = ttk.Frame(bottom_frame)
            plot_frame.grid(row=0, column=1, sticky='nsew', padx=(8,4), pady=4)
    except Exception:
        plot_frame = ttk.Frame(bottom_frame)
        plot_frame.grid(row=0, column=1, sticky='nsew', padx=(8,4), pady=4)

    plot_canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    plot_canvas.draw()
    plot_widget = plot_canvas.get_tk_widget()
    plot_widget.pack(fill='both', expand=True)

def clear_entries():
    try:
        if messagebox.askokcancel("Confirmation", "Are you sure you want to clear all entries?"):
            weight_entry.delete(0, tk.END)
            height_entry.delete(0, tk.END)
            age_entry.delete(0, tk.END)
            name_entry.delete(0, tk.END)
            try:
                gender_var.set('Male')
            except Exception:
                pass
            try:
                bodybuilder_var.set(0)
            except Exception:
                pass
            try:
                expectant_var.set(0)
            except Exception:
                pass
            try:
                toggle_expectant_check()
            except Exception:
                pass
            try:
                profiles_tree.selection_remove(profiles_tree.selection())
            except Exception:
                pass
            try:
                goal_bmi_entry.delete(0, tk.END)
            except Exception:
                pass
            result_label.config(text="", foreground="black")
            # Clear plot area too
            try:
                global plot_canvas, plot_toolbar
                if plot_toolbar:
                    plot_toolbar.destroy()
                    plot_toolbar = None
            except Exception:
                pass
            try:
                if plot_canvas:
                    plot_canvas.get_tk_widget().destroy()
                    plot_canvas = None
            except Exception:
                pass
    except Exception as e:
        # Handle the exception gracefully
        messagebox.showerror("Error", f"An error occurred: {e}")

def toggle_expectant_check(*args):
    if gender_var.get() == "Female":
        try:
            expectant_check.state(["!disabled"])
        except Exception:
            expectant_check.config(state="normal")
    else:
        try:
            expectant_check.state(["disabled"])
        except Exception:
            expectant_check.config(state="disabled")
        expectant_var.set(0)

def change_theme(theme):
    apply_theme(theme)

def export_report():
    try:
        name = name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter your name.")
            return

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
                    pdf.set_auto_page_break(auto=True, margin=12)

                    # Set font
                    pdf.set_font("Arial", size=12)

                    # Title page with summary
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(0, 10, 'BMI Report', ln=True, align='C')
                    pdf.ln(4)
                    pdf.set_font("Arial", size=12)

                    def _s(text):
                        # sanitize text for latin-1 PDF output
                        if text is None:
                            return ''
                        # common replacements
                        replacements = {
                            '\u2014': '-', '\u2013': '-', '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u00A0': ' '
                        }
                        for k, v in replacements.items():
                            text = text.replace(k, v)
                        text = unicodedata.normalize('NFKD', str(text))
                        try:
                            text.encode('latin-1')
                            return text
                        except UnicodeEncodeError:
                            return text.encode('latin-1', 'replace').decode('latin-1')

                    pdf.cell(0, 8, _s(f'Name: {name}'), ln=True)
                    pdf.cell(0, 8, _s(f'Weight: {weight} kg'), ln=True)
                    pdf.cell(0, 8, _s(f'Height: {height} m'), ln=True)
                    pdf.cell(0, 8, _s(f'Age: {age}'), ln=True)
                    pdf.cell(0, 8, _s(f'Gender: {gender}'), ln=True)
                    pdf.cell(0, 8, _s(f'BMI: {bmi:.2f}'), ln=True)
                    pdf.cell(0, 8, _s(f'Weight Status: {status}'), ln=True)
                    pdf.ln(6)

                    # Detailed advice and plan
                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(0, 8, 'Detailed Advice:', ln=True)
                    pdf.set_font("Arial", size=11)
                    txt_advice = globals().get('last_advice_text') or advice
                    # sanitize detailed advice
                    try:
                        txt_advice = unicodedata.normalize('NFKD', str(txt_advice))
                    except Exception:
                        txt_advice = str(txt_advice)
                    replacements = {'\u2014': '-', '\u2013': '-', '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u00A0': ' '}
                    for k, v in replacements.items():
                        txt_advice = txt_advice.replace(k, v)
                    try:
                        txt_advice.encode('latin-1')
                    except UnicodeEncodeError:
                        txt_advice = txt_advice.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 6, txt=txt_advice)

                    # Generate and include plots (trend + BMI categories)
                    if not ensure_matplotlib():
                        return
                    tmp_files = []
                    try:
                        # Trend image for this profile
                        def _generate_trend_image(pname):
                            profiles_local = load_profiles_file()
                            profile_local = profiles_local.get(pname)
                            if not profile_local:
                                return None
                            history = profile_local.get('history', [])
                            if not history:
                                return None
                            def _get_ts(h):
                                return h.get('timestamp') or h.get('date')

                            hist_sorted = sorted(history, key=lambda x: _get_ts(x) or '')
                            dates = []
                            weights = []
                            bmis = []
                            for h in hist_sorted:
                                ts = _get_ts(h)
                                if not ts:
                                    continue
                                try:
                                    dt = datetime.fromisoformat(ts)
                                except Exception:
                                    continue
                                dates.append(dt)
                                weights.append(h.get('weight', 0))
                                bmis.append(h.get('bmi', 0))
                            if not dates:
                                return None
                            fig = Figure(figsize=(10, 4), dpi=150)
                            ax1 = fig.add_subplot(111)
                            ax1.plot(dates, weights, 'o-', label='Weight (kg)')
                            ax1.set_ylabel('Weight (kg)')
                            ax2 = ax1.twinx()
                            ax2.plot(dates, bmis, 's-', color='orange', label='BMI')
                            ax2.set_ylabel('BMI')
                            ax1.set_xlabel('Date')
                            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                            fig.autofmt_xdate()
                            lines1, labels1 = ax1.get_legend_handles_labels()
                            lines2, labels2 = ax2.get_legend_handles_labels()
                            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
                            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                            fig.savefig(tmp.name, bbox_inches='tight')
                            tmp.close()
                            return tmp.name

                        def _generate_bmi_categories_image(user_bmi_val):
                            fig = Figure(figsize=(8, 3), dpi=150)
                            ax = fig.add_subplot(111)
                            bars = ax.bar(list(BMI_CATEGORIES.keys()), BMI_VALUES, color=BMI_COLORS)
                            ax.plot([-0.5, len(list(BMI_CATEGORIES.keys())) - 0.5], [user_bmi_val, user_bmi_val], color='blue', linestyle='--', label='Your BMI')
                            ax.set_xlabel('BMI Categories')
                            ax.set_ylabel('BMI Value')
                            ax.set_title('BMI Categories')
                            ax.grid(True)
                            ax.legend()
                            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                            fig.savefig(tmp.name, bbox_inches='tight')
                            tmp.close()
                            return tmp.name

                        trend_img = _generate_trend_image(name)
                        if trend_img:
                            tmp_files.append(trend_img)
                            pdf.add_page()
                            pdf.set_font('Arial', 'B', 12)
                            pdf.cell(0, 8, 'Trend: Weight and BMI over time', ln=True)
                            pdf.image(trend_img, x=10, y=30, w=pdf.w - 20)

                        bmi_img = _generate_bmi_categories_image(bmi)
                        if bmi_img:
                            tmp_files.append(bmi_img)
                            pdf.add_page()
                            pdf.set_font('Arial', 'B', 12)
                            pdf.cell(0, 8, 'BMI Categories (with your BMI)', ln=True)
                            pdf.image(bmi_img, x=10, y=30, w=pdf.w - 20)

                    finally:
                        # Save PDF first, then attempt to clean up temp files
                        pdf.output(export_file)
                        for tf in tmp_files:
                            try:
                                os.remove(tf)
                            except Exception:
                                pass

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


def add_history_entry(name, weight, height, bmi, age=None, gender=None, bodybuilder=None, expectant=None):
    """Append a timestamped measurement to the named profile's history (creates profile if missing)."""
    try:
        if not name:
            return
        profiles = load_profiles_file()
        profile = profiles.get(name, {})
        history = profile.get('history', [])
        history.append({'timestamp': datetime.utcnow().isoformat(), 'weight': float(weight), 'height': float(height), 'bmi': float(bmi)})
        # Ensure core fields exist
        profile.update({
            'name': name,
            'weight': str(weight),
            'height': str(height),
            'age': age if age is not None else profile.get('age', ''),
            'gender': gender if gender is not None else profile.get('gender', 'Male'),
            'bodybuilder': bodybuilder if bodybuilder is not None else profile.get('bodybuilder', 0),
            'expectant': expectant if expectant is not None else profile.get('expectant', 0),
            'history': history,
            'saved_at': datetime.utcnow().isoformat()
        })
        profiles[name] = profile
        save_profiles_file(profiles)
        update_profiles_view()
    except Exception:
        pass


def plot_profile_history(profile_name):
    """Plot stored weight and BMI over time for a given profile."""
    if not ensure_matplotlib():
        return
    try:
        profiles = load_profiles_file()
        profile = profiles.get(profile_name)
        if not profile:
            messagebox.showerror('Error', f'Profile "{profile_name}" not found.')
            return
        history = profile.get('history', [])
        if not history:
            messagebox.showinfo('No Data', f'No history for profile "{profile_name}".')
            return

        def _get_ts(h):
            return h.get('timestamp') or h.get('date')

        # Sort by timestamp/date and ignore invalid records
        history_sorted = sorted(history, key=lambda x: _get_ts(x) or '')
        dates = []
        weights = []
        bmis = []
        for h in history_sorted:
            ts = _get_ts(h)
            if not ts:
                continue
            try:
                dt = datetime.fromisoformat(ts)
            except Exception:
                continue
            dates.append(dt)
            weights.append(h.get('weight', 0))
            bmis.append(h.get('bmi', 0))
        if not dates:
            messagebox.showinfo('No Data', f'No valid timestamps for profile "{profile_name}".')
            return

        plt.close('all')
        fig = Figure(figsize=(6, 4), dpi=100)
        ax1 = fig.add_subplot(111)
        ax1.plot(dates, weights, 'o-', label='Weight (kg)')
        ax1.set_ylabel('Weight (kg)')
        ax2 = ax1.twinx()
        ax2.plot(dates, bmis, 's-', color='orange', label='BMI')
        ax2.set_ylabel('BMI')
        ax1.set_xlabel('Date')
        fig.autofmt_xdate()
        # Legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        # Embed in existing plot_frame
        global plot_canvas, plot_frame, plot_toolbar
        try:
            if plot_canvas:
                plot_canvas.get_tk_widget().destroy()
        except Exception:
            pass

        try:
            if plot_toolbar:
                plot_toolbar.destroy()
        except Exception:
            pass

        plot_canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        plot_canvas.draw()
        plot_widget = plot_canvas.get_tk_widget()
        plot_widget.pack(fill='both', expand=True)

        # Add toolbar for basic interactivity
        try:
            plot_toolbar = NavigationToolbar2Tk(plot_canvas, plot_frame)
            plot_toolbar.update()
            plot_toolbar.pack(side='bottom', fill='x')
        except Exception:
            pass

    except Exception as e:
        messagebox.showerror('Error', f'Failed to plot history: {e}')


def _compute_linear_slope(history, key):
    """Compute slope (units per day) for a numeric key in history list using simple linear regression."""
    try:
        if not history or len(history) < 2:
            return None
        xs = []
        ys = []
        for h in history:
            ts = h.get('timestamp') or h.get('date')
            if not ts:
                continue
            try:
                dt = datetime.fromisoformat(ts)
            except Exception:
                continue
            xs.append(dt.timestamp() / 86400.0)  # days
            ys.append(float(h.get(key, 0)))
        if len(xs) < 2:
            return None
        x_mean = sum(xs) / len(xs)
        y_mean = sum(ys) / len(ys)
        num = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(xs, ys))
        den = sum((xi - x_mean) ** 2 for xi in xs)
        if den == 0:
            return None
        slope = num / den  # units per day
        return slope
    except Exception:
        return None


def estimate_eta_for_profile(profile_name, goal_bmi=None):
    """Estimate ETA (in days) to reach a BMI goal using linear trend from history.

    Returns (eta_days, weekly_target) or (None, None) if cannot estimate.
    """
    try:
        profiles = load_profiles_file()
        profile = profiles.get(profile_name)
        if not profile:
            return None, None
        history = profile.get('history', [])
        if not history or len(history) < 2:
            return None, None

        if goal_bmi is None:
            return None, None

        slope = _compute_linear_slope(history, 'bmi')
        current = float(history[-1].get('bmi', 0))
        target = float(goal_bmi)

        if slope is None or slope == 0:
            return None, None

        # days needed (target - current) / slope
        days = (target - current) / slope
        # If slope moves away from target (days negative), return None
        if days < 0:
            return None, None

        # weekly target (bmi/week)
        weekly_target = (target - current) / (days / 7.0) if days != 0 else None
        return int(days), weekly_target
    except Exception:
        return None, None


def set_goal_for_selected():
    name = name_entry.get().strip()
    if not name:
        sel = profiles_tree.focus()
        if not sel:
            selection = profiles_tree.selection()
            if selection:
                sel = selection[0]
        if not sel:
            messagebox.showerror('Error', 'No profile selected or name entered.')
            return
        name = sel

    try:
        gb = goal_bmi_entry.get().strip()
        if not gb:
            messagebox.showerror('Error', 'Please enter a goal BMI.')
            return
        profiles = load_profiles_file()
        profile = profiles.get(name, {})
        goal = profile.get('goal', {})
        goal['bmi'] = float(gb)
        # Remove any legacy weight goal to keep BMI-only goals
        goal.pop('weight', None)
        goal['set_at'] = datetime.utcnow().isoformat()
        profile['goal'] = goal
        profiles[name] = profile
        save_profiles_file(profiles)
        update_profiles_view()
        messagebox.showinfo('Saved', f'Goal BMI saved for profile "{name}".')
    except Exception as e:
        messagebox.showerror('Error', f'Failed to save goal: {e}')


def show_eta_for_selected():
    sel = profiles_tree.focus()
    if not sel:
        selection = profiles_tree.selection()
        if selection:
            sel = selection[0]
    name = sel or name_entry.get().strip()
    if not name:
        messagebox.showerror('Error', 'No profile selected or name entered.')
        return

    profiles = load_profiles_file()
    profile = profiles.get(name)
    if not profile:
        messagebox.showerror('Error', f'Profile "{name}" not found.')
        return

    goal = profile.get('goal', {})
    gb = goal.get('bmi')
    if gb is None:
        messagebox.showinfo('No Goal', 'No BMI goal set for this profile. Enter a Goal BMI and click Save Goal.')
        return

    days, weekly = estimate_eta_for_profile(name, goal_bmi=gb)
    if days is None:
        messagebox.showinfo('Unable to estimate', 'Insufficient history or no clear trend to estimate ETA.')
        return

    weeks = days / 7.0
    parts = []
    parts.append(f"Target BMI: {gb}")
    parts.append(f"Estimated time: {days} days (~{weeks:.1f} weeks)")
    if weekly is not None:
        parts.append(f"Required weekly change: {weekly:.2f} per week")

    messagebox.showinfo('ETA & Targets', '\n'.join(parts))


def generate_goal_plan(profile_name, weeks=12):
    """Generate a week-by-week micro-plan to reach the saved BMI goal for a profile.

    Returns a formatted string describing weekly targets and sample action items.
    """
    try:
        profiles = load_profiles_file()
        profile = profiles.get(profile_name)
        if not profile:
            return ''
        goal = profile.get('goal', {})
        if not goal:
            return ''

        history = profile.get('history', [])
        # Determine current baseline value
        if history:
            last = history[-1]
            current_bmi = float(last.get('bmi', 0))
        else:
            try:
                current_bmi = float(profile.get('bmi') or 0)
            except Exception:
                current_bmi = 0

        gb = goal.get('bmi')
        if gb is None:
            return ''

        days, weekly_required = estimate_eta_for_profile(profile_name, goal_bmi=gb)
        current = current_bmi
        target = float(gb)

        if weekly_required is None:
            return 'Insufficient history or unclear trend to generate a goal plan.'

        lines = []
        lines.append(f"Current BMI: {current:.2f}")
        lines.append(f"Target BMI: {target:.2f}")
        lines.append(f"Required weekly change: {weekly_required:.2f} BMI/week")

        lines.append('')
        lines.append('12-week micro-plan (weekly target):')
        for w in range(1, weeks + 1):
            expected = current + weekly_required * w
            lines.append(f" Week {w:2d}: target BMI ~ {expected:.2f}")

        lines.append('')
        lines.append('Actionable recommendations:')
        lines.append('- Aim for 2-3 strength sessions per week and 2-3 moderate cardio sessions.')
        lines.append('- Prioritize progressive overload for muscle maintenance/growth; add low-impact cardio for fat loss.')

        lines.append('')
        lines.append('Weekly checklist:')
        lines.append('- Track BMI once per week at the same time of day.')
        lines.append('- Prepare 2-3 meals in advance (meal prep).')
        lines.append('- Complete at least one strength session and two shorter activity sessions.')

        return '\n'.join(lines)
    except Exception:
        return ''


def show_trend_for_selected():
    sel = profiles_tree.focus()
    if not sel:
        selection = profiles_tree.selection()
        if selection:
            sel = selection[0]
    if sel:
        plot_profile_history(sel)
    else:
        name = name_entry.get().strip()
        if name:
            plot_profile_history(name)
        else:
            messagebox.showerror('Error', 'No profile selected or name entered.')

# Create the main window (use ttkbootstrap if available)
if USE_TTB and _style is not None:
    root = _style.master
    root.title("Personal Health Assistant")
else:
    root = tk.Tk()
    root.title("Personal Health Assistant")
try:
    _icon_path = os.path.join(base_path, "PersonalHealthAssistant.ico")
    if os.path.exists(_icon_path):
        root.iconbitmap(_icon_path)
except Exception:
    pass
window_width = 800
window_height = 800
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = int((screen_width / 2) - (window_width / 2))
y_coordinate = int((screen_height / 2) - (window_height / 2))
# Open fullscreen / maximized by default. On Windows use 'zoomed', otherwise try fullscreen attribute.
try:
    root.state('zoomed')
except Exception:
    try:
        root.attributes('-fullscreen', True)
    except Exception:
        root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

# Create a modern, responsive layout using frames and grid
label_font = ("Segoe UI", 11)
entry_font = ("Segoe UI", 11)

# Modernize styles: use ttkbootstrap when available, otherwise tweak ttk styles
style = ttk.Style()
try:
    style.configure('TButton', padding=8, relief='flat', font=entry_font)
    style.configure('TLabel', font=label_font)
    style.configure('TEntry', padding=4)
    style.configure('Card.TLabelframe', background=DEFAULT_THEME['bg'], borderwidth=0, relief='flat', padding=10)
    style.configure('Card.TLabelframe.Label', font=label_font)
except Exception:
    pass

def make_button(parent, text, command=None):
    """Create a modern-looking button; prefer ttkbootstrap if available."""
    if USE_TTB:
        try:
            return tb.Button(parent, text=text, bootstyle='primary', command=command)
        except Exception:
            return ttk.Button(parent, text=text, command=command)
    else:
        return ttk.Button(parent, text=text, command=command)

# top-level container
main_frame = ttk.Frame(root, padding=12)
main_frame.pack(fill='both', expand=True)

# Left: input / actions
left_frame = ttk.LabelFrame(main_frame, text='Input', padding=10, style='Card.TLabelframe')
left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 8), pady=(0, 8))

# Right: profiles
right_frame = ttk.LabelFrame(main_frame, text='Profiles', padding=10, style='Card.TLabelframe')
right_frame.grid(row=0, column=1, sticky='nsew', padx=(8, 0), pady=(0, 8))

# Bottom: results / plot
bottom_frame = ttk.LabelFrame(main_frame, text='Results', padding=10, style='Card.TLabelframe')
bottom_frame.grid(row=1, column=0, columnspan=2, sticky='nsew')

main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=0)
main_frame.rowconfigure(1, weight=1)

# Input widgets in left_frame using grid
ttk.Label(left_frame, text='Name:', font=label_font).grid(row=0, column=0, sticky='w')
name_entry = ttk.Entry(left_frame, font=entry_font)
name_entry.grid(row=0, column=1, sticky='ew', padx=6, pady=2)

ttk.Label(left_frame, text='Mass (kg):', font=label_font).grid(row=1, column=0, sticky='w')
weight_entry = ttk.Entry(left_frame, font=entry_font)
weight_entry.grid(row=1, column=1, sticky='ew', padx=6, pady=2)

ttk.Label(left_frame, text='Height (m):', font=label_font).grid(row=2, column=0, sticky='w')
height_entry = ttk.Entry(left_frame, font=entry_font)
height_entry.grid(row=2, column=1, sticky='ew', padx=6, pady=2)

ttk.Label(left_frame, text='Age:', font=label_font).grid(row=3, column=0, sticky='w')
age_entry = ttk.Entry(left_frame, font=entry_font)
age_entry.grid(row=3, column=1, sticky='ew', padx=6, pady=2)

ttk.Label(left_frame, text='Gender:', font=label_font).grid(row=4, column=0, sticky='w')
gender_var = tk.StringVar(left_frame)
gender_var.set('Male')
gender_menu = ttk.Combobox(left_frame, textvariable=gender_var, values=('Male', 'Female'), state='readonly', font=entry_font)
gender_menu.grid(row=4, column=1, sticky='ew', padx=6, pady=2)
gender_menu.bind('<<ComboboxSelected>>', lambda e: toggle_expectant_check())

expectant_var = tk.IntVar()
expectant_check = ttk.Checkbutton(left_frame, text='Expectant Mother', variable=expectant_var)
expectant_check.state(['disabled']) if gender_var.get() != 'Female' else None
expectant_check.grid(row=5, column=0, columnspan=2, sticky='w', pady=(4, 2))

bodybuilder_var = tk.IntVar()
bodybuilder_check = ttk.Checkbutton(left_frame, text='Bodybuilder', variable=bodybuilder_var)
bodybuilder_check.grid(row=6, column=0, columnspan=2, sticky='w', pady=(0, 6))

# Goal inputs (BMI only)
ttk.Label(left_frame, text='Goal BMI:', font=label_font).grid(row=7, column=0, sticky='w')
goal_bmi_entry = ttk.Entry(left_frame, font=entry_font)
goal_bmi_entry.grid(row=7, column=1, sticky='ew', padx=6, pady=2)

left_frame.columnconfigure(1, weight=1)

# Buttons in left_frame
btn_frame = ttk.Frame(left_frame)
btn_frame.grid(row=10, column=0, columnspan=2, pady=6)
calculate_button = make_button(btn_frame, text='Calculate BMI', command=calculate_and_show_bmi)
calculate_button.grid(row=0, column=0, padx=6, pady=2)
clear_button = make_button(btn_frame, text='Clear', command=clear_entries)
clear_button.grid(row=0, column=1, padx=6, pady=2)
export_button = make_button(btn_frame, text='Export Report', command=export_report)
export_button.grid(row=0, column=2, padx=6, pady=2)
# Detailed advice viewer button
def show_detailed_advice():
    try:
        text = last_advice_text
    except Exception:
        text = ''
    if not text:
        messagebox.showinfo('No Advice', 'No detailed advice available. Calculate BMI first.')
        return

    # Toplevel window with scrollable Text widget
    top = tk.Toplevel(root)
    top.title('Detailed Advice')
    top.geometry('700x500')
    txt = tk.Text(top, wrap='word', padx=8, pady=8)
    scr = ttk.Scrollbar(top, orient='vertical', command=txt.yview)
    txt.configure(yscrollcommand=scr.set)
    txt.insert('1.0', text)
    txt.config(state='disabled')
    txt.pack(side='left', fill='both', expand=True)
    scr.pack(side='right', fill='y')

def show_history():
    name = name_entry.get().strip()
    if not name:
        messagebox.showinfo('No Name', 'Please enter a name to view history.')
        return
    try:
        profiles = load_profiles_file()
        profile = profiles.get(name, {})
        history = profile.get('history', [])
        if not history:
            messagebox.showinfo('No History', f'No history found for {name}.')
            return
        text = f"History for {name}:\n\n"
        for entry in history:
            text += f"Date: {entry.get('date', 'Unknown')}\n"
            text += f"Weight: {entry.get('weight', 'Unknown')} kg, Height: {entry.get('height', 'Unknown')} m, BMI: {entry.get('bmi', 'Unknown')}\n"
            text += f"Category: {entry.get('category', 'Unknown')}, Gender: {entry.get('gender', 'Unknown')}, Age: {entry.get('age', 'Unknown')}\n"
            text += f"Bodybuilder: {'Yes' if entry.get('bodybuilder', False) else 'No'}, Expectant: {'Yes' if entry.get('expectant', False) else 'No'}\n\n"
    except Exception as e:
        text = f"Error loading history: {e}"

    # Toplevel window with scrollable Text widget
    top = tk.Toplevel(root)
    top.title('History')
    top.geometry('700x500')
    txt = tk.Text(top, wrap='word', padx=8, pady=8)
    scr = ttk.Scrollbar(top, orient='vertical', command=txt.yview)
    txt.configure(yscrollcommand=scr.set)
    txt.insert('1.0', text)
    txt.config(state='disabled')
    txt.pack(side='left', fill='both', expand=True)
    scr.pack(side='right', fill='y')

detailed_button = make_button(btn_frame, text='Detailed Advice', command=show_detailed_advice)
detailed_button.grid(row=0, column=3, padx=6, pady=2)

history_button = make_button(btn_frame, text='View History', command=show_history)
history_button.grid(row=0, column=4, padx=6, pady=2)

# Profiles in right_frame
profiles_frame = ttk.Frame(right_frame)
profiles_frame.pack(fill='both', expand=True)
profiles_tree = ttk.Treeview(profiles_frame, columns=('name', 'age', 'gender', 'saved_at'), show='headings', height=12)
profiles_tree.heading('name', text='Name')
profiles_tree.heading('age', text='Age')
profiles_tree.heading('gender', text='Gender')
profiles_tree.heading('saved_at', text='Saved At')
profiles_tree.column('name', width=160)
profiles_tree.column('age', width=60)
profiles_tree.column('gender', width=80)
profiles_tree.column('saved_at', width=140)
profiles_tree.pack(side='left', fill='both', expand=True)

profiles_scroll = ttk.Scrollbar(profiles_frame, orient='vertical', command=profiles_tree.yview)
profiles_tree.configure(yscrollcommand=profiles_scroll.set)
profiles_scroll.pack(side='right', fill='y')

action_frame = ttk.Frame(right_frame)
action_frame.pack(fill='x', pady=(6, 0))
save_profile_button = make_button(action_frame, text='Save Profile', command=save_profile)
save_profile_button.pack(side='left', padx=6, pady=4)
load_profile_button = make_button(action_frame, text='Load Profile', command=load_selected_profile)
load_profile_button.pack(side='left', padx=6, pady=4)
delete_profile_button = make_button(action_frame, text='Delete Profile', command=delete_profile)
delete_profile_button.pack(side='left', padx=6, pady=4)
show_trend_button = make_button(action_frame, text='Show Trend', command=show_trend_for_selected)
show_trend_button.pack(side='left', padx=6, pady=4)
set_goal_button = make_button(action_frame, text='Save Goal', command=lambda: set_goal_for_selected())
set_goal_button.pack(side='left', padx=6, pady=4)
show_eta_button = make_button(action_frame, text='Show ETA', command=lambda: show_eta_for_selected())
show_eta_button.pack(side='left', padx=6, pady=4)

profiles_tree.bind('<Double-1>', lambda e: load_selected_profile())
root.after(50, update_profiles_view)

# Results and embedded plot in bottom_frame
# Create two sub-frames so results appear bottom-left and graph bottom-right
results_frame = ttk.Frame(bottom_frame)
results_frame.grid(row=0, column=0, sticky='nsew', padx=(4, 8), pady=4)
plot_frame = ttk.Frame(bottom_frame)
plot_frame.grid(row=0, column=1, sticky='nsew', padx=(8, 4), pady=4)

bottom_frame.columnconfigure(0, weight=1)
bottom_frame.columnconfigure(1, weight=1)
bottom_frame.rowconfigure(0, weight=1)

result_label = ttk.Label(results_frame, text='', wraplength=400)
result_label.pack(fill='both', expand=True)

# Theme selector
theme_var = tk.StringVar(root)
theme_var.set('Default')
theme_menu = ttk.Combobox(main_frame, textvariable=theme_var, values=('Default', 'Alternate'), state='readonly', width=12)
theme_menu.grid(row=0, column=2, sticky='ne', padx=(8,0))
theme_menu.bind('<<ComboboxSelected>>', lambda e: change_theme(theme_var.get()))

# Apply default theme initially
apply_theme('Default')

# keyboard shortcuts
root.bind('<Control-s>', lambda e: save_profile())
root.bind('<Control-l>', lambda e: load_selected_profile())
root.bind('<Control-q>', lambda e: root.quit())

if __name__ == '__main__':
    # Run the main event loop
    root.mainloop()



