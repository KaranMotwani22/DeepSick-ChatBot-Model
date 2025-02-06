class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        }

        this.state = false;
        this.messages = [];
        this.isProcessing = false;  // Flag to check if a message is being processed
    }

    getCurrentUrl() {
        console.log("Sent")
        var id = localStorage.getItem("EmpID")
        fetch('http://127.0.0.1:5000/save_url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({code: "done"})
        })
        .then(r => r.json())
        .then(r => {
             localStorage.setItem('assistant_id', r.answer)
            })
        } else {
            chatbox.classList.remove('chatbox--active')
        }
        ;
    }

    diffPageUrl() {
        console.log("Sent1")
        var a_id = localStorage.getItem("assistant_id")
        fetch('http://127.0.0.1:5000/get_id', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({code: a_id })
        })
        .then(r => r.json())
        .then(r => {
             localStorage.setItem('assistant_id', r.answer)
            })
        } else {
            chatbox.classList.remove('chatbox--active')
        }
        ;
    }

    display() {
        const {openButton, chatBox, sendButton} = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox))

        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox)
            }
        })
    }

    toggleState(chatbox) {
        this.state = !this.state;
        // show or hides the box
        if(this.state) {
            var textField = chatbox.querySelector('input');
            let text1 = textField.value

            chatbox.classList.add('chatbox--active')
            console.log("Started")
            fetch('http://127.0.0.1:5000/nudge', {
                method: 'POST',
                body: JSON.stringify({ message: text1 }),
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json'
                },
            })
            .then(r => r.json())
            .then(r => {
                let msg2 = { name: "Sam", message: r.answer };
                this.messages.push(msg2);
                this.updateChatText(chatbox)
                textField.value = ''
            })
        } else {
            chatbox.classList.remove('chatbox--active')
        }
    }

    onSendButton(chatbox) {
        if (this.isProcessing) return;  // Prevent sending if already processing a message

        var textField = chatbox.querySelector('input');
        let text1 = textField.value
        if (text1 === ""){
            return;
        }

        this.isProcessing = true;  // Set the flag to indicate processing
        textField.disabled = true;  // Disable the input field
        this.args.sendButton.disabled = true;  // Disable the send button

        let msg1 = { name: "User", message: text1 }
        this.messages.push(msg1);

        fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then(r => r.json())
        .then(r => {
            let msg2 = { name: "Sam", message: r.answer };
            this.messages.push(msg2);
            this.updateChatText(chatbox)
            textField.value = ''
            this.isProcessing = false;  // Reset the flag
            textField.disabled = false;  // Re-enable the input field
            this.args.sendButton.disabled = false;  // Re-enable the send button
        }).catch((error) => {
            console.error('Error:', error);
            this.updateChatText(chatbox)
            textField.value = ''
            this.isProcessing = false;  // Reset the flag even if there is an error
            textField.disabled = false;  // Re-enable the input field
            this.args.sendButton.disabled = false;  // Re-enable the send button
        });
    }

    updateChatText(chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function(item, index) {
            if (item.name === "Sam") {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>'
            } else {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
            }
        });

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
        this.scrollToBottom(chatmessage);
    }

    scrollToBottom(chatmessage) {
        chatmessage.scrollTop = chatmessage.scrollHeight;
    }
}

const chatbox = new Chatbox();
chatbox.display();
chatbox.getCurrentUrl();
