To implement a **countdown timer** for an online exam system that works in real-time across refreshes and page closures, and also allows the teacher to monitor live progress, follow these steps:

---

### 1. **Store Exam Start Time and Duration in the Database**

You need to persist the exam start time and duration in the database to ensure the timer state is not lost.

Update the `Exam` model:

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Exam(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_time = models.DateTimeField(default=now)
    duration_minutes = models.PositiveIntegerField()
```

Store the **start time** when the student begins the exam and calculate the end time dynamically.

---

### 2. **Frontend Countdown Timer**

Use JavaScript to create a live countdown timer. Fetch the remaining time from the server and update the timer on the client-side.

Add a `take_exam` view to calculate the remaining time:

```python
from django.utils.timezone import now
from django.shortcuts import get_object_or_404

def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    end_time = exam.start_time + timedelta(minutes=exam.duration_minutes)
    remaining_time = (end_time - now()).total_seconds()

    # If the exam is over
    if remaining_time <= 0:
        return render(request, 'exam_over.html', {'exam': exam})

    questions = exam.questions.all()
    return render(request, 'take_exam.html', {
        'exam': exam,
        'questions': questions,
        'remaining_time': int(remaining_time),
    })
```

In `take_exam.html`, include JavaScript for the countdown:

```html
<script>
  let remainingTime = {{ remaining_time }};

  function startCountdown() {
      const timerElement = document.getElementById("timer");
      const interval = setInterval(() => {
          if (remainingTime <= 0) {
              clearInterval(interval);
              alert("Time is up!");
              window.location.href = "{% url 'exam_over' exam.id %}";
          } else {
              const minutes = Math.floor(remainingTime / 60);
              const seconds = remainingTime % 60;
              timerElement.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
              remainingTime--;
          }
      }, 1000);
  }

  window.onload = startCountdown;
</script>

<h2>Time Remaining: <span id="timer"></span></h2>
```

---

### 3. **Prevent Restarting on Refresh**

The `remaining_time` is calculated on the server side based on the `start_time`, so it will remain accurate across refreshes. Since the backend sends the correct remaining time on each page load, the countdown will not restart incorrectly.

---

### 4. **Prevent Timer Reset on Page Close**

To persist the timer state across sessions:

1. Store the exam start time in the database.
2. Ensure that the remaining time is fetched from the server when the page is loaded.

---

### 5. **Teacher Monitoring: Live Progress**

Use WebSockets with Django Channels to enable real-time updates for the teacher.

#### Install Django Channels:

```bash
pip install channels
```

#### Update `settings.py`:

```python
INSTALLED_APPS += ['channels']
ASGI_APPLICATION = 'exam_system.asgi.application'
```

#### Configure `asgi.py`:

```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from exams.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
```

#### Create a Consumer for Progress Updates:

In `exams/consumers.py`:

```python
import json
from channels.generic.websocket import WebsocketConsumer

class ExamProgressConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = 'exam_progress'
        self.accept()

        # Add the WebSocket connection to the group
        self.channel_layer.group_add(self.group_name, self.channel_name)

    def disconnect(self, close_code):
        # Remove the WebSocket connection from the group
        self.channel_layer.group_discard(self.group_name, self.channel_name)

    def receive(self, text_data):
        data = json.loads(text_data)
        # Broadcast the progress data to the group
        self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_progress',
                'message': data['message']
            }
        )

    def send_progress(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message
        }))
```

#### Configure WebSocket URLs:

In `exams/routing.py`:

```python
from django.urls import path
from .consumers import ExamProgressConsumer

websocket_urlpatterns = [
    path('ws/exam-progress/', ExamProgressConsumer.as_asgi()),
]
```

#### Frontend: Display Progress for Teachers

In the teacher's dashboard:

```html
<script>
  const socket = new WebSocket(
    "ws://" + window.location.host + "/ws/exam-progress/"
  );

  socket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    const progressElement = document.getElementById("progress");
    progressElement.textContent += data.message + "\n";
  };
</script>

<div id="progress">
  <h2>Live Exam Progress</h2>
</div>
```

#### Broadcast Student Progress:

Update student answers in real time:

```python
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def update_progress(user, exam, question, answered_correctly):
    channel_layer = get_channel_layer()
    message = f"Student {user.username} answered question {question.id} {'correctly' if answered_correctly else 'incorrectly'}"
    async_to_sync(channel_layer.group_send)(
        'exam_progress',
        {'type': 'send_progress', 'message': message}
    )
```

Call `update_progress` whenever a student answers a question.

---

This setup ensures:

1. The countdown timer persists across refreshes and page closures.
2. Teachers can see live progress and scores.
3. WebSockets enable real-time updates.
   **1. Project Setup (if not already done)**

- **Install required packages:**

  ```bash
  pip install channels daphne
  ```

- **Create a `channels` directory:**

  ```bash
  mkdir channels
  ```

- **Create `routing.py` within the `channels` directory:**

  ```python
  from django.urls import path
  from .consumers import ExamConsumer

  websocket_urlpatterns = [
      path('ws/exam/<int:exam_id>/', ExamConsumer.as_asgi()),
  ]
  ```

**2. Create a Consumer (in `channels.consumers.py`)**

```python
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core import serializers
from .models import Exam

class ExamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.exam_id = self.scope['url_route']['kwargs']['exam_id']
        self.room_group_name = f'exam_{self.exam_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        pass

    # Receive message from room group
    async def exam_timer(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'timer_update',
            'remaining_time': event['remaining_time'],
        }))

```

**3. Modify Views.py**

```python
from django.shortcuts import render
from .models import Exam
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def start_exam(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    end_time = datetime.datetime.now() + datetime.timedelta(minutes=exam.duration_minutes)
    request.session['exam_end_time'] = end_time.strftime("%Y-%m-%d %H:%M:%S")

    # Send initial timer update to connected clients
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'exam_{exam_id}',
        {
            'type': 'exam_timer',
            'remaining_time': calculate_remaining_time(end_time),
        }
    )

    return render(request, 'exam.html', {'exam': exam})

# Helper function to calculate remaining time
def calculate_remaining_time(end_time):
    now = datetime.datetime.now()
    remaining = end_time - now
    # ... (Format remaining time as needed) ...
    return formatted_remaining_time

```

**4. Create exam.html**

```html
<script>
  const ws = new WebSocket(
    "ws://" + window.location.host + "/ws/exam/{{ exam.id }}/"
  );

  ws.onmessage = function (event) {
    const data = JSON.parse(event.data);
    if (data["type"] === "timer_update") {
      const remainingTime = data["remaining_time"];
      // Update the timer display on the page
      document.getElementById("timer").textContent = remainingTime;
    }
  };
</script>

<div id="timer"></div>
```

**5. Run Development Server**

```bash
daphne -b 127.0.0.1 -p 8000 channels.routing
```

**Explanation**

- **WebSockets:** Establish a persistent connection between the client and server.
- **Channels:** Provides the framework for handling asynchronous communication within Django.
- **Consumers:** Handle WebSocket connections and messages.
- **Room Groups:** Allow you to efficiently broadcast messages to specific sets of clients.
- **Timer Updates:** The server calculates the remaining time and broadcasts it to all connected clients in the exam room.
- **Client-Side Handling:** JavaScript receives updates from the WebSocket and updates the timer display.

**Key Considerations:**

- **Synchronization:** While this approach provides real-time updates, minor discrepancies between the server and client-side timers might occur due to network latency and processing time.
- **Error Handling:** Implement robust error handling for WebSocket connections, network issues, and potential timing discrepancies.
- **Security:** Implement appropriate security measures to prevent unauthorized access and manipulation of the timer.

**Note:** This is a simplified example. You'll need to adapt it to your specific project needs, including:

- Implementing more robust timer calculations and updates.
- Handling exam submissions and user interactions.
- Adding features like automatic submission when the timer expires.
- Implementing security measures.

By using WebSockets and the Channels framework, you can achieve a highly responsive and accurate countdown timer in your Django-based online exam system.
