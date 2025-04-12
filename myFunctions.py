def send_mail(name, link, rec, amount, Message, mail):
    msg = Message(
        subject="Payment Received",
        recipients=[str(rec)],
        html=f'''<h3>Hello Mr./Ms. {name}, your payment of {amount} has been received.
            You can see your payment status on the link given below:
            </h3>
            <a href="{link}">Click here</a> 
            '''
    )
    mail.send(msg)


def addEnteryAndSendEmail(db, jsonify, name, email, amount, mail, Message):
    try:
        db.session.commit()

        try:
            send_mail(name=name, link="www.google.com", rec=email,
                      amount=amount, Message=Message, mail=mail)
            print("sending mail")
        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({"msg": "Entry added to database but email couldn't be sent."}), 400
    except Exception as e:
        print(f"An error occurred: {e}")
        db.session.rollback()
        return jsonify({"msg": "Data couldn't be added to the database. Please try again."}), 400
    return jsonify({"msg": "Success! Data added and email sent to the customer."}), 200
