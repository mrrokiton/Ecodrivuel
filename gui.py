from flask import Flask, render_template, url_for, redirect, flash, request
from settings import settings_values
import main
app = Flask(__name__)

app.config['SECRET_KEY'] = '1234567890'

@app.route("/settings", methods=['GET', 'POST'])
def settings():
    if request.method == "POST":
        fuel_type = request.form['fueltype']
        refuel_amount = request.form['refuel_amount']
        consumption = request.form['consumption']
        localization = request.form['localization']

        print(fuel_type)

        global result_data
        result_data = main.create_table(fuel_type, refuel_amount, consumption, localization)

        return redirect(url_for("result"))
    else:
        return render_template('settings.html', title = 'settings')

@app.route("/result")
def result():
    result_data_sorted = sorted(result_data, key=lambda x: float(x['total_costs']))
    return render_template('result.html', data=result_data_sorted)

@app.route("/importResult")
def importResult():
    return render_template('download.html')

@app.route("/", methods=['GET', 'POST'])
def hello():
    if request.method == "POST":
        main.download_data()

        return redirect(url_for("importResult"))
    else:
        return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)