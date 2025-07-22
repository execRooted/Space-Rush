// Space Rush Joystick Controller
// Works with Arduino Uno and similar boards

// Pin definitions
const int X_PIN = A0;    // Joystick X axis
const int Y_PIN = A1;    // Joystick Y axis
const int BUTTON_PIN = 2; // Joystick button

// Variables
int xValue = 0;
int yValue = 0;
int buttonState = 1; // Assuming active-low button (1 = not pressed)

void setup() {
  Serial.begin(9600);
  pinMode(BUTTON_PIN, INPUT_PULLUP); // Enable internal pull-up resistor for button
}

void loop() {
  // Read joystick values
  xValue = analogRead(X_PIN);
  yValue = analogRead(Y_PIN);
  buttonState = digitalRead(BUTTON_PIN);
  
  // Send data to computer in format: "X,Y,Button"
  Serial.print(xValue);
  Serial.print(",");
  Serial.print(yValue);
  Serial.print(",");
  Serial.println(buttonState);
  
  // Small delay to prevent flooding the serial port
  delay(20);
}
