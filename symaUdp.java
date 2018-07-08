import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.io.DataInputStream;
import java.io.IOException;
import java.util.*; 
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;
import java.io.*;
import java.net.*;
import java.awt.event.ActionListener;
import javax.swing.JTextField;
import javax.swing.AbstractAction;
import javax.swing.Action;

public class symaUdp extends javax.swing.JFrame implements java.awt.event.ActionListener, java.awt.event.KeyListener
{
  JButton btnNewButton;
  JLabel lblNotInitiated;
  JButton btnNewButton_1;
  JButton btnDecelerate;
  java.io.OutputStream dos;
  DatagramSocket client;
  DatagramPacket sendPkt;
  InetAddress ipAddr;
  int port;
  int lr;
  int fb;
  boolean lr_locked = false;
  boolean fb_locked = false;
  boolean sh_locked = false;
  boolean ht_locked = false;
  boolean rt_locked = false;
  int retries=10;
  boolean connected=false;
  int timeout=200;
  private JTextField textField;
  private JTextField textField_1;
  JButton btnEnable;
  JButton btnNewButton_4;
  Map<Character,String>sims = new HashMap<Character,String>();
  Map <String,Character> rev = new HashMap<String,Character>();

  Map <Character,Byte> hash = new HashMap<Character,Byte>();
  public symaUdp(){
	sims.put('j', "Roll");
	sims.put('o', "Roll");
	sims.put('l', "Roll");
	sims.put('4', "Roll");
	sims.put('6', "Roll");
	
	sims.put('i', "Pitch");
	sims.put('k', "Pitch");
	sims.put('p', "Pitch");
	sims.put('2', "Pitch");
	sims.put('8', "Pitch");
	
	sims.put('a', "Yaw");
	sims.put('f', "Yaw");
	sims.put('d', "Yaw");
	
	sims.put('q', "Throtle");
	sims.put('w', "Throtle");
	sims.put('e', "Throtle");
	sims.put('5', "Throtle");
	sims.put('0', "Throtle");
	
	sims.put('s', "Start");
	sims.put('b', "Bind");
	//sims.put(', value)
	
    setDefaultCloseOperation(3);
    getContentPane().setLayout(new javax.swing.BoxLayout(getContentPane(), 0));
    
    JPanel panel = new JPanel();
    getContentPane().add(panel);
    panel.setLayout(null);
    
    lblNotInitiated = new JLabel("Not Connected");
    lblNotInitiated.addKeyListener(this);
    lblNotInitiated.setFont(new java.awt.Font("Consolas", 1, 16));
    lblNotInitiated.setBounds(10, 11, 289, 36);
    panel.add(lblNotInitiated);
    
    btnNewButton = new JButton("Bind");
    btnNewButton.setBounds(118, 58, 89, 23);
    btnNewButton.addActionListener(this);
    btnNewButton.addKeyListener(this);
    panel.add(btnNewButton);
    
    btnNewButton_1 = new JButton("WakeUP");
    btnNewButton_1.setBounds(118, 92, 89, 23);
    btnNewButton_1.addActionListener(this);
    btnNewButton_1.addKeyListener(this);
    panel.add(btnNewButton_1);
    
    JButton btnLand = new JButton("Land");
    btnLand.addActionListener(this);
    btnLand.addKeyListener(this);
    btnLand.setBounds(118, 126, 89, 23);
    panel.add(btnLand);
    
    JButton btnHover = new JButton("Hold");
    btnHover.addActionListener(this);
    btnHover.addKeyListener(this);
    btnHover.setBounds(10, 126, 89, 23);
    panel.add(btnHover);
    
    btnDecelerate = new JButton("Connect");
    btnDecelerate.addActionListener(this);
    btnDecelerate.addKeyListener(this);
    btnDecelerate.setBounds(10, 58, 89, 23);
    panel.add(btnDecelerate);
    
    JButton btnHalt = new JButton("Emergency Landing");
    btnHalt.addActionListener(this);
    btnHalt.addKeyListener(this);
    btnHalt.setBounds(10, 160, 197, 46);
    panel.add(btnHalt);
    
    JButton btnFr = new JButton("^");
    btnFr.addMouseListener(new MouseAdapter()
    {
      public void mousePressed(MouseEvent e) {
        command('8');
      }
      
      public void mouseReleased(MouseEvent e) {
        command('p');
      }
    });
    btnFr.addKeyListener(this);
    btnFr.setBounds(289, 30, 55, 51);
    panel.add(btnFr);
    
    JButton btnNewButton_2 = new JButton("v");
    btnNewButton_2.addKeyListener(this);
    btnNewButton_2.addMouseListener(new MouseAdapter()
    {
      public void mousePressed(MouseEvent e) {
        command('2');
      }
      
      public void mouseReleased(MouseEvent e) {
        command('p');
      }
    });
    btnNewButton_2.setBounds(289, 126, 55, 51);
    panel.add(btnNewButton_2);
    
    JButton btnNewButton_3 = new JButton(">");
    btnNewButton_3.addKeyListener(this);
    btnNewButton_3.addMouseListener(new MouseAdapter()
    {
      public void mousePressed(MouseEvent e) {
        command('6');
      }
      
      public void mouseReleased(MouseEvent e) {
        command('o');
      }
    });
    btnNewButton_3.setBounds(341, 78, 55, 51);
    panel.add(btnNewButton_3);
    
    JButton button = new JButton("<");
    button.addMouseListener(new MouseAdapter()
    {
      public void mousePressed(MouseEvent e) {
        command('4');
      }
      
      public void mouseReleased(MouseEvent e) {
        command('o');
      }
    });
    button.addKeyListener(this);
    button.setBounds(235, 78, 55, 51);
    panel.add(button);
    
    JButton btnLift = new JButton("Lift");
    btnLift.setBounds(10, 92, 89, 23);
    panel.add(btnLift);
    btnLift.addActionListener(this);
    btnLift.addKeyListener(this);
    
    JButton btnO = new JButton("O");
    btnO.addActionListener(this);
    btnO.setBounds(289, 78, 55, 51);
    panel.add(btnO);
    btnO.addKeyListener(this); 
    
    JButton btnAnticlockwise = new JButton("CCW");
    btnAnticlockwise.addActionListener(this);
    btnAnticlockwise.setBounds(221, 188, 89, 23);
    btnAnticlockwise.addKeyListener(this);
    panel.add(btnAnticlockwise);
    
    JButton btnCw = new JButton("CW");
    btnCw.addActionListener(this);
    btnCw.setBounds(319, 188, 89, 23);
    btnCw.addKeyListener(this);
    panel.add(btnCw);
    
    textField = new JTextField();
    textField.setBounds(10, 261, 140, 20);
    panel.add(textField);
    textField.setColumns(10);
    
    textField_1 = new JTextField();
    textField_1.setText("1337");
    textField_1.setBounds(160, 261, 44, 20);
    panel.add(textField_1);
    textField_1.setColumns(10);
    
    btnEnable = new JButton("Enable AP");
    btnEnable.setBounds(10, 217, 197, 36);
    btnEnable.addActionListener(this);

    btnEnable.addKeyListener(this);
    panel.add(btnEnable);
    
    btnNewButton_4 = new JButton("Enable Debugging");
    btnNewButton_4.addActionListener(this);
    btnNewButton_4.setBounds(221, 217, 187, 36);
    btnNewButton_4.addKeyListener(this);
    panel.add(btnNewButton_4);
    

    
    setSize(437, 332);
    setVisible(true); 
  }
  
  public static void main(String[] args) {
    new symaUdp();
  }
  
  public void actionPerformed(ActionEvent e)
  {
	    if (e.getActionCommand() == "Bind") {
	        command('b');
	      }
	    else if (e.getActionCommand() == "CCW") {
	        command('a');
	      }
	    else if (e.getActionCommand() == "CW") {
	        command('d');
	      }
	    else if(e.getActionCommand() =="Enable AP" ){
	    	command('t');
	    	btnEnable.setText("Disable AP");
	    }
	    else if(e.getActionCommand() =="Disable AP" ){
	    	command('y');
	    	btnEnable.setText("Enable AP");
	    }
	    else if(e.getActionCommand()=="Enable Debugging") {
	    	command('+');
	    	btnNewButton_4.setText("Disable Debugging");
	    }
	    else if(e.getActionCommand()=="Disable Debugging") {
	    	command('!');
	    	btnNewButton_4.setText("Enable Debugging");
	    }
    else if (e.getActionCommand() == "WakeUP") {
      command('s');
    }
    else if (e.getActionCommand() == "Disconnect") {
     command('`');
     btnDecelerate.setText("Connect");
     btnNewButton_4.setText("Enable Debugging");
     btnEnable.setText("Enable AP");
     lblNotInitiated.setText("Disconnected");
     connected=false;
    }
    else if (e.getActionCommand() == "Hold") {
      command('w');
    } else if (e.getActionCommand() == "Land") {
      command('0');
    } else if (e.getActionCommand() == "Connect") {
    	connected=true;
    	Thread receiver = new Thread(new Runnable(){
    		
          public void run() {
    
      try {
    	  client = new DatagramSocket();
    	  ipAddr = InetAddress.getByName("localhost");
    	  try {
    	  ipAddr = InetAddress.getByName(textField.getText());
    	  }
    	  catch(Exception ex){
    		  System.out.println("invalid ip");
    	  }
    	  port = Integer.parseInt(textField_1.getText());
    	  port = port==0?1337:port;
    	  sendPkt = new DatagramPacket("ping".getBytes(),4,ipAddr,port);
    	  client.send(sendPkt);
    	  lblNotInitiated.setText("Req Sent.");
    	  byte[] buff=new byte[1024];
    	  DatagramPacket pk=new DatagramPacket(buff,1024);
    	  while(connected) {   		  
    		  client.receive(pk);
    		  hash.put((char)buff[3],buff[5]);
    		  if(pk.getLength()>7)
    			  lblNotInitiated.setText(new String(buff, 7, pk.getLength()-7));
    	  }
      }
      catch(Exception ex) {
      
        lblNotInitiated.setText("Unable To connect");
        System.out.println(ex);
      
    }
          }
    });
    	receiver.start();
    	try {
			Thread.sleep(500);
		} catch (InterruptedException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
    	Thread keepAlive =new Thread(new Runnable() {
    		public void run() {
    			while(connected) {
    				command('|');
    				try{
    					Thread.sleep(4000);
    				}
    				catch(Exception e) {
    				}
    			}
    		}
  });
    	keepAlive.start();
    	btnDecelerate.setText("Disconnect");
    }
  else if (e.getActionCommand() == "MaxThrtl") {
      command('q');
    } else if (e.getActionCommand() == "Emergency Landing") {
      command('e');
    } else if (e.getActionCommand() == "O") {
      command('w');
    } else if (e.getActionCommand() == "Lift") {
      command('5');
    } else if (e.getActionCommand() == "Fall") {
      command('0');
    } }
  
  void command(char code) {
	
	  Thread dm = new Thread(new Runnable(){
		  
		 public void run() {
			 
	  byte[]dataArray= "me-x-c-".getBytes();
	  dataArray[3]=(byte)code;
	  Random ad = new Random();
	  dataArray[5] = (byte) ad.nextInt(127);
	  
	  DatagramPacket cpkt = new DatagramPacket(dataArray,7,ipAddr,port);
	  String mode = sims.get(code); 
	  if(mode!=null) {
		  rev.put(mode, code); 
	  }
	  for(int i=0;i<retries;i++) {
      try {
        client.send(cpkt);
        System.out.println("sent: " + code);
        Thread.sleep(timeout);
      } catch (IOException e1) {
        e1.printStackTrace();
      }
      catch (InterruptedException e) {
		e.printStackTrace();
      }
      if(mode !=null)
	      if (code!=rev.get(mode)) {
	    	  break;
	      }
	  if(hash.get(code)!=null) 
		  if(hash.get(code)==dataArray[5]){
	    	  break;
	      }
	  }
  }
  });
	  dm.start();
  }
  
  public void keyPressed(KeyEvent arg0)
  {
    
	switch (arg0.getKeyCode()) {
    case 38: 
      if (!fb_locked) {
        command(arg0.isShiftDown() ? '8' : 'i');
        fb = 56;
        fb_locked = true;
      }
      break;
    case 40: 
      if (!fb_locked) {
        command(arg0.isShiftDown() ? '2' : 'k');
        fb = 50;
        fb_locked = true;
      }
      break;
    case 37: 
      if (!lr_locked) {
        command(arg0.isShiftDown() ? '4' : 'j');
        lr = 52;
        lr_locked = true;
      }
      break;
    case 39: 
      if (!lr_locked) {
        command(arg0.isShiftDown() ? '6' : 'l');
        lr = 54;
        lr_locked = true;
      }
      break;
      
      
    case 81: 
    	if(!ht_locked) {
    		command('5');
    		ht_locked=true;
    	}
        break;
  
    case 69: 
    	if(!ht_locked) {
    	command('0');
    	ht_locked=true;
    	}
        break;
    case 65:
    	if(!rt_locked) {
    	command('a');
    	rt_locked=true;
    	}
    	break;
    case 68:
    	if(!rt_locked) {
    	command('d');
    	rt_locked=true;
    	}
    	break;
    case 16: 
      if (!sh_locked) {
        if (fb != 0) {
          command((char)fb);
        }
        if (lr != 0) {
          command((char)lr);
        }
        sh_locked = true;
      }
      break;
    case 90:
    	command('e');
    	break;
    }
    //System.out.println(arg0.getKeyCode());
  }
  
  public void keyReleased(KeyEvent e)
  {
    switch (e.getKeyCode())
    {
    case 38: 
    case 40: 
      command('p'); // forward-backward- normal
      fb = 0;
      fb_locked = false;
      break;
    
    case 37: 
    case 39: 
      command('o'); // left-right normal
      lr = 0;
      lr_locked = false;
      break;
    
    case 16: 
      if (fb != 0) {
        command(fb == 56 ? 'i' : 'k');
      }
      if (lr != 0) {
        command(lr == 52 ? 'j' : 'l');
      }
      sh_locked = false;
      break;
      
    case 81:
    case 69:
    	ht_locked=false;
    	command('w');
    	break;
    	
    case 65:
    case 68:
    	rt_locked=false;
    	command('f');
    	break;
    }
  }
  
  public void keyTyped(KeyEvent e) {}

}