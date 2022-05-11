#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

Adafruit_SSD1306 display(4); //OLED_RESET 4

#if (SSD1306_LCDHEIGHT != 32)
#error("Height incorrect, change Adafruit_SSD1306.h");
#endif

void setup()   {
  Serial.begin(9600);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);  //define I2C Adress
  display.clearDisplay();
}
void loop() {
  long runtime = millis() / 1000;
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(25, 0);
  display.println("Hello world!");
  display.setTextColor(WHITE);
  display.setTextSize(2);
  display.println(runtime);
  display.setTextSize(1);
  display.setTextColor(BLACK, WHITE); //Change Background to White
  display.setCursor(20, 25);
  display.println("WWW.AEQ-WEB.COM");
  display.display();
  display.clearDisplay();
}
