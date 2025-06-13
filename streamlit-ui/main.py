import streamlit as st
import pandas as pd
import requests
import os
import io

menu = st.sidebar.selectbox("Menu", ["Home", "About", "Contact"])


def generate_excel_file(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Loan Schedule")
    return output.getvalue()


def format_numbers_with_commas(df: pd.DataFrame) -> pd.DataFrame:
    df_formatted = df.copy()
    currency_cols = [
        "Payment",
        "Principal Paid",
        "Interest Paid",
        "Remaining Balance",
        "Cumulative Interest",
        "Cumulative Principal",
    ]
    for col in currency_cols:
        df_formatted[col] = df_formatted[col].apply(lambda x: f"{x:,.2f}")
    return df_formatted


if menu == "Home":
    st.title("🏠 Salary Advance Loan Calculator")
    frequency_options = {"Monthly": 1, "Quarterly": 3, "Semi-Annually": 6, "Yearly": 12}
    with st.form("advance_form"):
        st.subheader("Advance Loan Details")
        salary = st.number_input(
            "Enter Income/Salary", min_value=0.0, step=0.01, format="%.2f"
        )
        frequency_str = st.selectbox(
            "Select Frequency", options=list(frequency_options.keys())
        )
        frequency = frequency_options[frequency_str]
        loan_amount = st.number_input(
            "Enter Loan Amount", min_value=0.0, step=0.01, format="%.2f"
        )
        advance_submit_button = st.form_submit_button("Calculate")

    if advance_submit_button:
        if loan_amount > 0 and salary > 0:
            backend_url = os.getenv("BACKEND_URL")
            try:
                response = requests.post(
                    f"{backend_url}/calculate_advance",
                    json={
                        "salary": salary,
                        "frequency": frequency,
                        "loan_amount": loan_amount,
                    },
                )
                response.raise_for_status()  # Raises HTTPError for 4xx/5xx
                schedule = response.json()
                st.session_state["requested_loan_amount"] = schedule[
                    "requested_loan_amount"
                ]
                st.session_state["max_loan_amount"] = schedule["max_loan_amount"]
                st.success(
                    f"Requested Loan Amount: ${schedule['requested_loan_amount']}\n"
                )
                st.success(
                    f"Eligible Maximum Loan Amount: ${schedule['max_loan_amount']}"
                )
            except requests.exceptions.HTTPError as err:
                if response.status_code == 400:
                    st.error(
                        f"❌ {response.json().get('detail', 'An error occurred.')}"
                    )
                else:
                    st.error("❌ Server error. Please try again later.")
                st.stop()
            except requests.exceptions.RequestException as err:
                st.error("❌ Unable to connect to backend service.")
                st.stop()

        else:
            st.error("Please enter valid values for all fields.")

    if "requested_loan_amount" in st.session_state:

        with st.form("loan_form"):
            st.subheader("Compute Loan Schedule")
            loan_amount = st.number_input(
                "Enter Loan Amount",
                min_value=0.0,
                step=0.01,
                value=float(st.session_state.requested_loan_amount.replace(",", "")),
            )

            interest_rate = st.number_input(
                "Enter Interest Rate (%)", min_value=12.0, step=0.1
            )
            loan_term = st.number_input("Enter Loan Term (Months)", min_value=3, step=1)
            submit_button = st.form_submit_button("Calculate")
        if submit_button:
            if loan_amount > 0 and interest_rate >= 0 and loan_term > 0:
                backend_url = os.getenv("BACKEND_URL")
                response = requests.post(
                    f"{backend_url}/calculate_loan",
                    json={
                        "loan_amount": loan_amount,
                        "interest_rate": interest_rate,
                        "loan_term": loan_term,
                    },
                )
                if response.status_code == 200:
                    df = pd.DataFrame(response.json())
                    st.session_state["schedule"] = df
                else:
                    st.error("Error calculating loan details.")
            else:
                st.error("Please enter valid values for all fields.")

    # Adding option to download the loan schedule either in raw or formatted form
    if "schedule" in st.session_state:
        schedule_df = st.session_state["schedule"]
        st.dataframe(format_numbers_with_commas(schedule_df))

        excel_data = generate_excel_file(schedule_df)

        format_choice = st.radio(
            "Download Format:", ["Raw (numeric)", "Formatted (with commas)"]
        )

        df_to_download = (
            schedule_df
            if format_choice == "Raw (numeric)"
            else format_numbers_with_commas(schedule_df)
        )
        excel_data = generate_excel_file(df_to_download)

        st.download_button(
            label="📥 Download Loan Schedule as Excel",
            data=excel_data,
            file_name="loan_schedule.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
elif menu == "About":
    st.title("ℹ️ About")
elif menu == "Contact":
    st.title("📞 Contact")
