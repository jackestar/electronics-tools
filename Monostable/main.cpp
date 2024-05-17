#include <iostream>
#include <cmath>

#define ln3 1.098612289

using namespace std;

int main(int argc, char const *argv[]) {

	int in = 0;
	if (argc == 2) {in = strtol(argv[1],NULL,0);}
    while (in==0 && cout << "Valor de tiempo deseado (seg): " && !(cin >> in)) {
        cin.clear(); //clear bad input flag
        cin.ignore(numeric_limits<streamsize>::max(), '\n'); //discard input
        cout << "Valor Invalido ";
    }

	int vc[] = {10,12,15,18,22,27,33,39,47,51,56,68,82};

	double rv = 0;
	double cv = 0;
	double time = 0;

    // Exponential
    unsigned int exp = 7;

    unsigned int rmin = 25; // small values damage NE555

	for (int s = 0; s < exp; ++s) {
			int pots = 1*pow(10,s);

			for (double r:vc) {
				r = r*pots;
                // cout<<endl<<r<<"R value testing\n";
                // else cout<<"Pass through";
				for (int i = 0; i < exp; ++i) {
					int poti = 1*pow(10,i);
					for (double c:vc) {
						c = c*0.000001*poti;
						double temp = ln3*r*c;
                        if (r>=rmin) {
						    if (abs(in - temp) == abs(in - time)) {
						    	bool kt = false;
						    	bool ut = false;
						    	if (r>1000) {
						    		kt =true;
						    		r = r/1000;
						    	}
						    	if (c<0.01) {
						    		ut =true;
						    		c = c*1000000;
						    	}
						    	cout<<"coincidencia en tiempo: "<<temp<<"\n r: "<<r<<(kt?char('k'):' ')<<" c: "<<c<<(ut?char('u'):' ')<<endl;
						    }
						    else if (abs(in - temp) < abs(in - time)) {
						    	time = temp;
						    	rv = r;
						    	cv = c;
						    }
                        }
					}
				}
			}
		}

	bool k = false;
	bool u = false;
	if (rv>1000) {
		k =true;
		rv = rv/1000;
	}
	if (cv<0.01) {
		u =true;
		cv = cv*1000000;
	}
	cout<<"\n\nResistencia: "<<rv<<(k?char('k'):' ');
	cout<<"\nCapacitor: "<<cv<<(u?char('u'):' ');
	cout<<"\nValor: "<<time<<endl;

	return 0;
}