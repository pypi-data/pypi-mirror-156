import os

b="\033[1;35m"
g="\033[1;32m"
w="\033[1;37m"

def logo ():
  os.system("clear")
  os.system("""echo '  ░█████╗░██╗░░██╗██╗░░██╗██╗░░░██╗░█████╗░██╗░░░██╗
  ██╔══██╗██║░██╔╝╚██╗██╔╝██║░░░██║██╔══██╗██║░░░██║
  ███████║█████═╝░░╚███╔╝░╚██╗░██╔╝███████║██║░░░██║
  ██╔══██║██╔═██╗░░██╔██╗░░╚████╔╝░██╔══██║██║░░░██║
  ██║░░██║██║░╚██╗██╔╝╚██╗░░╚██╔╝░░██║░░██║╚██████╔╝
  ╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░╚═╝░╚═════╝░
----------------------------------------------------
  ╔════════════════════════════════════════════════╗
  ║      😈IF YOU ARE BAD THAN I AM YOUR DAD😈     ║
  ║             Hacking is Not A Crime             ║
  ║               Its A profession.                ║
  ╚════════════════════════════════════════════════╝
----------------------------------------------------'|lolcat""")

def main ():
  logo ()
  os.system("echo '\t[1] FACEBOOK\n\t[2] GITHUB\n\t[3] FACEBOOK PAGE\n\t[4] FACEBOOK GROUP\n\t[5] TOXIC-VIRUS\n\t[6] INSTAGRAM\n\t[7] TWITTER\n\t[8] PYPI\n\t[0] EXIT' | lolcat")
  ()
  inp = str(input(w+"\n\t["+b+"?"+w+"]"+g+" SELECT YOUR OPTION :"+b+" "))
  if inp == "1":
    os.system("xdg-open https://facebook.com/AKXVAU")
    main ()
  elif inp == "2":
    os.system("xdg-open https://facebook.com/AKX.THE.PSYCHO")
    main ()
  elif inp == "3":
    os.system("xdg-open https://github.com/AKXVAU")
    main ()
  elif inp == "4":
    os.system("xdg-open https://www.facebook.com/groups/2078563798832259/?ref=share")
    main ()
  elif inp == "5":
    os.system("xdg-open https://facebook.com/toxicvirus21")
    main ()
  elif inp == "6":
    os.system("xdg-open https://instagram.com/AKXVAU")
    main ()
  elif inp == "7":
    os.system("xdg-open https://twitter.com/ITZAKX21")
    main ()
  elif inp == "0":
    sys.exit()
  else:
    main ()
    
    
main ()