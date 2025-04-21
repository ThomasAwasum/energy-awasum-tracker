import streamlit as st
import time
import datetime
import pandas as pd
import plotly.express as px
import numpy as np
import streamlit.components.v1 as components

# -------------------------------
# CSS for styling buttons, interface, and persistent chat bubble
# -------------------------------
st.markdown("""
<style>
/* General button focus styling */
div.stButton button:focus {
    outline: none;
    box-shadow: none;
}

/* Style the Start button (if used elsewhere) */
#start-button-container button {
    background-color: #d32f2f !important;
    color: white !important;
    border: none;
    border-radius: 8px;
    padding: 12px 30px;
    font-size: 18px;
    transition: background-color 0.3s ease;
}
#start-button-container button:hover {
    background-color: #b71c1c !important;
}

/* Persistent chat bubble styling */
#chatbubble-container {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 350px;
    height: 520px;
    z-index: 10000;
    border: none;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    border-radius: 10px;
    overflow: hidden;
}

/* Optional: Style the main container for a professional look */
.reportview-container {
    background: linear-gradient(135deg, #1e3c72, #2a5298);
    color: white;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Initialize session state variables
# -------------------------------
# Set page to "main" directly, bypassing login.
if 'page' not in st.session_state:
    st.session_state.page = "main"
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["timestamp", "hour", "energy"])
if 'selected_energy' not in st.session_state:
    st.session_state.selected_energy = None
if 'simulated_data' not in st.session_state:
    st.session_state.simulated_data = None
if 'tasks' not in st.session_state:
    st.session_state.tasks = []  # For task scheduling
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []  # For potential future use

# Callback to remove a task
def remove_task(index):
    tasks = st.session_state.tasks
    if 0 <= index < len(tasks):
        tasks.pop(index)
    st.session_state.tasks = tasks

# -------------------------------
# MAIN DASHBOARD PAGE (No Login Page)
# -------------------------------
if st.session_state.page == "main":
    st.sidebar.title("Dashboard")
    # Four tabs: Energy Tracker, Energy Graph, Task Scheduler, Chat Bot
    page_choice = st.sidebar.radio("Select Tab:", 
                                   ["Energy Tracker", "Energy Graph", "Task Scheduler", "Chat Bot"])

    # ENERGY TRACKER TAB
    if page_choice == "Energy Tracker":
        st.header("Energy Tracker")
        st.write("This is where you track your energy levels (Response).")
        st.subheader("What's your current energy level?")
        def toggle_option(option_value):
            st.session_state.selected_energy = option_value if st.session_state.selected_energy != option_value else None
        if st.button(f"{'●' if st.session_state.selected_energy==4 else '○'} 4 (Awesome)", key="option_4", on_click=toggle_option, args=(4,)):
            pass
        if st.button(f"{'●' if st.session_state.selected_energy==3 else '○'} 3 (Pretty ok)", key="option_3", on_click=toggle_option, args=(3,)):
            pass
        if st.button(f"{'●' if st.session_state.selected_energy==2 else '○'} 2 (Sluggish)", key="option_2", on_click=toggle_option, args=(2,)):
            pass
        if st.button(f"{'●' if st.session_state.selected_energy==1 else '○'} 1 (Absolutely Awful)", key="option_1", on_click=toggle_option, args=(1,)):
            pass
        if st.session_state.selected_energy is not None:
            if st.button("Submit Response", key="submit_response"):
                now = datetime.datetime.now()
                hour_val = now.hour
                energy_val = st.session_state.selected_energy
                new_row = {"timestamp": now, "hour": hour_val, "energy": energy_val}
                st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
                st.success("Response recorded!")
                st.session_state.selected_energy = None

    # ENERGY GRAPH TAB
    elif page_choice == "Energy Graph":
        st.header("Energy Graph")
        st.write("View your energy data (Results).")
        if not st.session_state.data.empty:
            avg_energy = st.session_state.data.groupby("hour")["energy"].mean().reset_index()
            fig = px.line(avg_energy, x="hour", y="energy", markers=True, title="Average Hourly Energy Levels")
            fig.update_layout(xaxis=dict(range=[0, 23], dtick=1),
                              yaxis=dict(range=[1, 4], dtick=1),
                              plot_bgcolor='rgba(0,0,0,0)',
                              paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})
        else:
            st.write("No energy data available yet. Please record your energy levels.")
        
        st.subheader("Simulation")
        sim_toggle = st.checkbox("Show Simulation", value=False, key="sim_toggle")
        if sim_toggle:
            sim_sample = st.selectbox("Select sample user:", 
                                      ["Morning person", "Night owl", "Multiple spikes and valleys", "No discernible pattern"])
            def simulate_morning_person(hour):
                base = 3.8 if 6 <= hour <= 10 else 2.0
                noise = np.random.uniform(-0.2, 0.2)
                return round(max(1.0, min(4.0, base + noise)), 1)
            def simulate_night_owl(hour):
                base = 3.8 if 18 <= hour <= 23 else 2.0
                noise = np.random.uniform(-0.2, 0.2)
                return round(max(1.0, min(4.0, base + noise)), 1)
            def simulate_spikes_valleys(hour):
                base = 2.5 + 1.0 * np.sin(2 * np.pi * hour / 24)
                noise = np.random.uniform(-0.5, 0.5)
                return round(max(1.0, min(4.0, base + noise)), 1)
            def simulate_no_pattern(hour):
                return round(np.random.uniform(1, 4), 1)
            if sim_sample == "Morning person":
                sim_func = simulate_morning_person
            elif sim_sample == "Night owl":
                sim_func = simulate_night_owl
            elif sim_sample == "Multiple spikes and valleys":
                sim_func = simulate_spikes_valleys
            else:
                sim_func = simulate_no_pattern
            st.write(f"Simulating data for: {sim_sample}")
            energy_values = [sim_func(hr) for hr in range(24)]
            rows = []
            for frame in range(24):
                for hr in range(frame + 1):
                    rows.append({"hour": hr, "energy": energy_values[hr], "frame": frame})
            simulated_data = pd.DataFrame(rows)
            st.session_state.simulated_data = simulated_data[simulated_data["frame"]==23].reset_index(drop=True)
            fig = px.line(simulated_data, x="hour", y="energy", markers=True,
                          animation_frame="frame",
                          title=f"Simulated Average Hourly Energy Levels - {sim_sample}")
            fig.update_layout(xaxis=dict(range=[0, 23], dtick=1),
                              yaxis=dict(range=[1, 4], dtick=1),
                              plot_bgcolor='rgba(0,0,0,0)',
                              paper_bgcolor='rgba(0,0,0,0)',
                              transition={'duration': 10})
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})

    # TASK SCHEDULER TAB
    elif page_choice == "Task Scheduler":
        st.header("Task Scheduler")
        st.write("Plan your day by adding tasks and receiving scheduling recommendations based on simulated energy data.")
        sim_sample = st.selectbox("Select sample user for scheduling:", 
                                  ["Morning person", "Night owl", "Multiple spikes and valleys", "No discernible pattern"],
                                  key="chat_sim_sample")
        if st.button("Generate Simulated Data for Scheduling", key="gen_sim_data"):
            def simulate_morning_person(hour):
                base = 3.8 if 6 <= hour <= 10 else 2.0
                noise = np.random.uniform(-0.2, 0.2)
                return round(max(1.0, min(4.0, base + noise)), 1)
            def simulate_night_owl(hour):
                base = 3.8 if 18 <= hour <= 23 else 2.0
                noise = np.random.uniform(-0.2, 0.2)
                return round(max(1.0, min(4.0, base + noise)), 1)
            def simulate_spikes_valleys(hour):
                base = 2.5 + 1.0 * np.sin(2 * np.pi * hour / 24)
                noise = np.random.uniform(-0.5, 0.5)
                return round(max(1.0, min(4.0, base + noise)), 1)
            def simulate_no_pattern(hour):
                return round(np.random.uniform(1, 4), 1)
            if sim_sample == "Morning person":
                sim_func = simulate_morning_person
            elif sim_sample == "Night owl":
                sim_func = simulate_night_owl
            elif sim_sample == "Multiple spikes and valleys":
                sim_func = simulate_spikes_valleys
            else:
                sim_func = simulate_no_pattern
            hours = list(range(24))
            energy_values = [sim_func(hr) for hr in hours]
            sim_df = pd.DataFrame({"hour": hours, "energy": energy_values})
            st.session_state.simulated_data = sim_df
            st.success("Simulated data generated for scheduling.")
        
        if st.session_state.simulated_data is not None:
            st.subheader("Simulated Energy Graph for Scheduling")
            df = st.session_state.simulated_data
            fig = px.line(df, x="hour", y="energy", markers=True, title=f"Simulated Energy Levels - {sim_sample}")
            fig.update_layout(xaxis=dict(range=[0, 23], dtick=1),
                              yaxis=dict(range=[1, 4], dtick=1),
                              plot_bgcolor='rgba(0,0,0,0)',
                              paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Add Tasks for Your Day")
        task_categories = {
            "Academic Tasks": {
                "Homework & Assignments": [
                    "Completing homework for each subject",
                    "Working on group projects or individual assignments",
                    "Reviewing and editing homework before submission"
                ],
                "Studying & Revision": [
                    "Intensive study sessions for exams and quizzes",
                    "Revising lecture notes or textbook chapters",
                    "Using flashcards or spaced repetition techniques"
                ],
                "Research & Writing": [
                    "Drafting essays, research papers, or lab reports",
                    "Outlining or brainstorming ideas for creative writing projects",
                    "Preparing presentations or posters"
                ]
            },
            "Creative & Extracurricular Tasks": {
                "Creative Projects": [
                    "Writing stories, poetry, or maintaining a journal",
                    "Sketching, painting, or digital art creation",
                    "Composing music or practicing an instrument"
                ],
                "Extracurricular Activities": [
                    "Rehearsals for drama or music",
                    "Practicing sports or dance routines",
                    "Participating in clubs, debates, or community projects"
                ]
            },
            "Physical & Health-Related Activities": {
                "Exercise & Sports": [
                    "Gym workouts, running, or cycling",
                    "Team sports practice or individual training sessions",
                    "Stretching, yoga, or other fitness classes"
                ],
                "Sleep & Personal Care": {
                    "Sleep": [
                        "Sleep"
                    ]
                }
            },
            "Household & Daily Living Tasks": {
                "Chores & Organization": [
                    "Cleaning or tidying your room/study area",
                    "Cooking, meal planning, or grocery shopping",
                    "Managing laundry and other household responsibilities"
                ],
                "Personal Management": [
                    "Scheduling daily routines and time management tasks",
                    "Budgeting, paying bills, or managing personal finances",
                    "Setting reminders for appointments and important deadlines"
                ]
            },
            "Social & Recreational Tasks": {
                "Social Engagement": [
                    "Attending social events, club meetings, or study groups",
                    "Organizing or participating in extracurricular clubs or volunteer work",
                    "Networking and building professional relationships"
                ],
                "Recreational & Relaxation": [
                    "Watching a movie or playing video games in moderation",
                    "Taking breaks for leisure reading or hobbies",
                    "Planning outings with friends or family"
                ]
            },
            "Sleep": {
                "Sleep": [
                    "Sleep"
                ]
            }
        }
        task_category = st.selectbox("Select Category", list(task_categories.keys()), key="task_cat_new")
        if isinstance(task_categories[task_category], dict):
            subcats = list(task_categories[task_category].keys())
            task_subcat = st.selectbox("Select Sub-category", subcats, key="task_subcat_new")
            spec_tasks = task_categories[task_category][task_subcat]
        else:
            task_subcat = None
            spec_tasks = task_categories[task_category]
        task_specific = st.selectbox("Select Specific Task", spec_tasks, key="task_spec_new")
        if task_category == "Sleep":
            task_duration = 8
            st.info("Sleep duration is fixed at 8 hours for scheduling purposes.")
        else:
            task_duration = st.number_input("Enter Task Duration (in hours, integer)", min_value=1, max_value=8, step=1, key="task_duration_new")
        if st.button("Add Task"):
            new_task = {
                "category": task_category,
                "subcategory": task_subcat if task_subcat else "",
                "specific": task_specific,
                "duration": task_duration
            }
            st.session_state.tasks.append(new_task)
            st.success(f"Added task: {task_specific} ({task_duration} hrs)")
        
        if st.session_state.tasks:
            st.subheader("Tasks for the Day")
            for i, t in enumerate(st.session_state.tasks, start=1):
                cols = st.columns([0.8, 0.2])
                cols[0].write(f"{i}. {t['specific']} ({t['duration']} hrs) - [{t['category']}" +
                              (f" > {t['subcategory']}]" if t['subcategory'] else "]"))
                if cols[1].button("Remove", key=f"remove_{i}", on_click=remove_task, args=(i-1,)):
                    pass
        
        if st.button("Generate Schedule"):
            if st.session_state.simulated_data is None:
                st.error("Please generate simulated data first in the Energy Graph tab.")
            elif not st.session_state.tasks:
                st.error("Please add at least one task.")
            else:
                df = st.session_state.simulated_data.copy()
                free_hours = list(range(24))
                schedule_recommendations = []
                def get_segments(hours_list):
                    segments = []
                    current_seg = []
                    for hr in sorted(hours_list):
                        if not current_seg or hr == current_seg[-1] + 1:
                            current_seg.append(hr)
                        else:
                            segments.append(current_seg)
                            current_seg = [hr]
                    if current_seg:
                        segments.append(current_seg)
                    return segments
                for task in st.session_state.tasks:
                    duration = int(task["duration"])
                    if task["specific"] == "Sleep":
                        segments = get_segments(free_hours)
                        best_block = None
                        best_avg = float('inf')
                        for seg in segments:
                            if len(seg) >= duration:
                                for i in range(len(seg) - duration + 1):
                                    block = seg[i:i+duration]
                                    avg_e = df[df["hour"].isin(block)]["energy"].mean()
                                    if avg_e < best_avg:
                                        best_avg = avg_e
                                        best_block = block
                        if best_block:
                            recommendation = {"task": task["specific"], "duration": duration, "start": best_block[0], "end": best_block[-1] + 1, "block": best_block}
                            for hr in best_block:
                                free_hours.remove(hr)
                        else:
                            recommendation = {"task": task["specific"], "duration": duration, "start": None, "end": None, "block": None}
                        schedule_recommendations.append(recommendation)
                    else:
                        segments = get_segments(free_hours)
                        best_block = None
                        best_avg = -float('inf')
                        for seg in segments:
                            if len(seg) >= duration:
                                for i in range(len(seg) - duration + 1):
                                    block = seg[i:i+duration]
                                    avg_e = df[df["hour"].isin(block)]["energy"].mean()
                                    if avg_e > best_avg:
                                        best_avg = avg_e
                                        best_block = block
                        if best_block:
                            recommendation = {"task": task["specific"], "duration": duration, "time": best_block[0], "block": best_block}
                            for hr in best_block:
                                free_hours.remove(hr)
                        else:
                            recommendation = {"task": task["specific"], "duration": duration, "time": None, "block": None}
                        schedule_recommendations.append(recommendation)
                st.subheader("Schedule Recommendations")
                for rec in schedule_recommendations:
                    if rec["task"] == "Sleep" and rec["start"] is not None:
                        st.write(f"Task: {rec['task']}, Duration: {rec['duration']} hrs. Recommended block: {int(rec['start'])}:00 to {int(rec['end'])}:00")
                    elif rec.get("time") is not None:
                        st.write(f"Task: {rec['task']}, Duration: {rec['duration']} hrs. Recommended block: {rec['block'][0]}:00 to {rec['block'][-1]+1}:00")
                    else:
                        st.write(f"Task: {rec['task']}, Duration: {rec['duration']} hrs. No available time slot found.")
                
                fig = px.line(df, x="hour", y="energy", markers=True, title=f"Simulated Energy Levels - {sim_sample}")
                fig.update_layout(
                    xaxis=dict(range=[0, 23], dtick=1),
                    yaxis=dict(range=[1, 4], dtick=1),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                colors = ["red", "blue", "green", "purple", "orange", "brown"]
                color_index = 0
                for rec in schedule_recommendations:
                    if rec["task"] == "Sleep" and rec["start"] is not None:
                        fig.add_shape(
                            type="rect",
                            x0=rec["start"], y0=1,
                            x1=rec["end"], y1=4,
                            fillcolor="yellow", opacity=0.3, line_width=0
                        )
                    elif rec.get("block") is not None:
                        fig.add_shape(
                            type="rect",
                            x0=rec["block"][0], y0=1,
                            x1=rec["block"][-1] + 1, y1=4,
                            fillcolor=colors[color_index % len(colors)],
                            opacity=0.3, line_width=0
                        )
                        color_index += 1
                st.plotly_chart(fig, use_container_width=True)

    # CHAT BOT TAB
    elif page_choice == "Chat Bot":
        st.header("Chat Bot")
        st.write("Chat with our assistant via the Chatbase widget below:")
        persistent_chat_html = """
<div id="persistent-chat" style="position: fixed; bottom: 20px; right: 20px; width: 350px; height: 500px; z-index: 10000; border: none;">
  <div id="chatbase-container"></div>
  <script>
  (function(){
    if(!window.chatbase || window.chatbase("getState") !== "initialized"){
      window.chatbase = (...args) => {
        if(!window.chatbase.q){ window.chatbase.q = []; }
        window.chatbase.q.push(args);
      };
      window.chatbase = new Proxy(window.chatbase, {
        get(target, prop){
          if(prop === "q"){ return target.q; }
          return (...args) => target(prop, ...args);
        }
      });
    }
    const onLoad = function(){
      const script = document.createElement("script");
      script.src = "https://www.chatbase.co/embed.min.js";
      script.id = "MdwqEnO0QpWV58ghfAv37";
      script.domain = "www.chatbase.co";
      document.body.appendChild(script);
    };
    if(document.readyState === "complete"){
      onLoad();
    } else {
      window.addEventListener("load", onLoad);
    }
  })();
  </script>
</div>
"""
        components.html(persistent_chat_html, height=520, width=370)

# -------------------------------
# End of Code
# -------------------------------
