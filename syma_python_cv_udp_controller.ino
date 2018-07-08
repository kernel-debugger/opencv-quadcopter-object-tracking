
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define throtle 0
#define gas 1
#define rotate 2
#define steering 3
#define debug 0

RF24 radio(3, 9);

const byte broadcastAddr[] ={0xab,0xac,0xad,0xae,0xaf};
const byte txAddr[] =       {0x46,0x83,0x20,0x12,0xA1};
byte       bindPkt[10]=     {0xa1,0x12,0x20,0x83,0x46,0xaa,0xaa,0xaa,0x00}; // cs =b1
const byte bindChans[]=     {0x10,0x20,0x30,0x40}; 
const byte comChans[]=      {0x11,0x21,0x31,0x41}; 
byte       anonPkt[10]=     {0x0A,0x1A,0x2A,0x3A,0x12,0x22,0x32,0x42,0xb1}; //cs = 0x46
byte       pkt[10]=         {0x7a,0x00,0x00,0x00,0x00,0x60,0x00,0x00,0x00};// cs = 6f 
byte pos[2]={};  
bool notify=true;
int debug2=0;
long last_channel_switched=0;
int channelNo=1;
int bound = 0; 
void setup(){

  Serial.begin(9600);
  radio.begin();
  radio.setDataRate(RF24_250KBPS);
  radio.setPayloadSize(10);
  radio.setAutoAck(false);
  radio.setPALevel(RF24_PA_LOW); //, RF24_PA_LOW, RF24_PA_HIGH and RF24_PA_MAX
  radio.setChannel(bindChans[0]);
  radio.stopListening();
  radio.openWritingPipe(broadcastAddr);
  radio.setCRCLength(RF24_CRC_16); // 2 Byte crc
  delay(1000);
  Serial.println("syma_python_cv_dup_controller");
}
void debuger(char alpha[]){
  Serial.println(alpha);
}

void altCoin(){
  
  long now=micros();
  if(now-last_channel_switched>7000){
   
        if(!bound){ 
          if(channelNo==sizeof(bindChans))
             channelNo=0;
           radio.setChannel(bindChans[channelNo]);
           channelNo++; 
        }
        else{
          if(channelNo==sizeof(comChans))
             channelNo=0;
          radio.setChannel(comChans[channelNo]);
           channelNo++;
        }
        
        last_channel_switched=micros();
  }
       if(debug)
        debuger("altCoin");
}

byte checksum(byte *data){
    byte sum = data[0];
   for (int ij=1; ij < 9; ij++)
      sum ^= data[ij];
   if(debug)
      debuger("checkSum");
   return sum + 0x55;
}
void sendPkt(byte *pekt){
    pekt[9] =checksum(pekt);  
    radio.write(pekt,10);
    if(debug)
      debuger("sendPkt");
}

void sendPktTill(byte *pekt,int till){
  long tm=millis();
  while(millis()-tm<till){
    sendPkt(pekt);
    altCoin();
  }
      if(debug)
      debuger("sendPktTill");
}

void bind_quad(){

  long mp=millis();
  bound = 0;
  radio.openWritingPipe(broadcastAddr);
  delay(100);
  Serial.println("Broadcasting...");
  while(millis()-mp<4000){ // 6 seconds
 
    sendPkt(bindPkt);
    sendPkt(anonPkt);
    altCoin();
   
  }
  notify=true;
  bound=1; // start sending data on the other address; cuz quad is bound
  radio.openWritingPipe(txAddr);
  Serial.println("Binding Completed...");
  delay(100);
  if(debug)
      debuger("bind");
}
 
void printPkt(){ 
       
    Serial.print("P:");
    Serial.print(pkt[gas],HEX);
    
    Serial.print(" \tR:");
    Serial.print(pkt[steering],HEX);
        
    Serial.print(" \tY:");
    Serial.print(pkt[rotate],HEX);

    Serial.print(" \tT:");
    Serial.println(pkt[throtle],HEX);
}

void loop(){  

  if(Serial.available()){
    
    Serial.readBytes(pos,2);  

    notify=true;

    switch((char)pos[0]){

//----------------------------------------------------
      case 't': //  throtle
              pkt[throtle]=pos[1];
              break;
              
//----------------------------------------------------

      case 'p': // pitch 
              pkt[gas]=pos[1];
              break;  
              
//----------------------------------------------------
      case 'r': // roll
              pkt[steering] =pos[1];
              break;   
              
//----------------------------------------------------
      case 'y': // yaw 
              pkt[rotate] =pos[1];
               break;   
                    
//----------------------------------------------------
      case 'b':  //  bind
              bind_quad();
              break;

//----------------------------------------------------
      case 'd':  //  debug
              debug2=pos[1];
              if(pos[1])
                Serial.println("Debugging Enabled");
              else
                Serial.println("Debugging Disabled");
              break;
              
//----------------------------------------------------
      case 's':   // start

              pkt[throtle] = 0xff;
              sendPktTill(pkt,1000);
              pkt[throtle] = 0x7a;
              sendPktTill(pkt, 1000);
              break;
              
//----------------------------------------------------
    }
  }
  if(bound){// if bound
    
    sendPkt(pkt);
    
    altCoin();
    
    if(notify && debug2){ // enable/disable debugging
     
       printPkt();
       notify=false;
       
    }
    
  }
  else if(notify ){
    Serial.println("Press initialize to bind");
    notify=false;
  }
}

