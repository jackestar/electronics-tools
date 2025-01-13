use std::env;
use std::{f64::INFINITY, vec};

const COMERCIAL_R: [f64; 39] = [
    1.0, 5.0, 6.4, 7.4, 10.0, 15.0, 27.0, 33.0, 40.0, 47.0, 50.0, 56.0, 82.0, 100.0, 150.0, 220.0,
    330.0, 470.0, 390.0, 560.0, 1e3, 2e3, 2.2e3, 2.7e3, 3.3e3, 4.7e3, 3.8e3, 10e3, 22e3, 33e3,
    47e3, 100e3, 220e3, 330e3, 680e3, 1e6, 1.8e6, 2.2e6, 6.2e6,
];
const COMERCIAL_C: [f64; 34] = [
    1e-9, 12e-9, 22e-9, 27e-9, 100e-9, 100e-9, 0.22e-6, 0.33e-6, 0.47e-6, 1e-6, 4.7e-6, 4.7e-6,
    10e-6, 22e-6, 27e-6, 33e-6, 33e-6, 47e-6, 47e-6, 47e-6, 100e-6, 100e-6, 100e-6, 100e-6, 220e-6,
    220e-6, 220e-6, 470e-6, 470e-6, 1800e-6, 1e-6, 20e-6, 330e-12, 22e-12,
];

fn main() {
    let args: Vec<String> = env::args().collect();
    let args_len = args.len();
    const MESSAGE: &str = "Uso: rc <number> [--show-all]\n";

    if args_len > 3 {
        print!("Demasiados argumentos\n{MESSAGE}");
    } else if args_len > 1 {
        let mut show_all = false;
        if args_len == 3 {
            show_all = &args[2] == "--show-all";
            if !show_all {
                print!("Argumento Invalido\n{MESSAGE}");
                return;
            }
        }
        let mut number_str = args[1].clone();
        let suffix = &number_str.chars().last().unwrap();

        // multiply suffix applied to number
        let proportion: f64 = match suffix {
            'k' | 'K'   => 1e3,
            'm'         => 1e-3,
            'u' | 'μ'   => 1e-6,
            'n'         => 1e-9,
            'p'         => 1e-12,
            _           => 1.0,
        };
        if proportion != 1.0 {
            number_str.pop();
        }

        let number: f64 = match number_str.parse() {
            Ok(n) => n,
            Err(_) => {
                print!("Ingrese un Numero Valido\n{MESSAGE}");
                return;
            }
        };

        // RC
        print!("R\tC\n");
        producto_cercano(&COMERCIAL_R, &COMERCIAL_C, number*proportion, show_all);

    } else {
        print!("Ingrese un valor como argumento\n{MESSAGE}");
    }
}
/// En base a dos listas busca cual es el producto mas cercano e imprime la lista de la combinación
/// de valores que mas se aproxima al resultado, el argumento show muestra la lista por orden de encuentro
/// este no muestra todas las posibles combinaciones
/// # Examples
/// ```
/// producto_cercano( [1.2,2.3,3.4] , [4.3,3.2,2,1] , 12.4)
/// ```
fn producto_cercano(lista1: &[f64], lista2: &[f64], valor: f64, show: bool) {
    let mut mejor_diferencia: f64 = INFINITY;
    let mut resultados: Vec<(f64, f64)> = Vec::new();
    for r in lista1 {
        for c in lista2 {
            let diferencia = (valor - r * c).abs();
            if diferencia < mejor_diferencia {
                mejor_diferencia = diferencia;
                if show {
                    resultados.push((*r, *c));
                } else {
                    resultados = vec![(*r, *c)]
                }
            } else if diferencia < mejor_diferencia {
                resultados.push((*r, *c));
            }
        }
    }

    // Print Result
    for resultado in &resultados {
        let test: Vec<_> = [(*resultado).0, (*resultado).1]
            .iter()
            .map(|&x| sufijo(x))
            .collect();
        test.iter().for_each(|x| print!("{x}\t"));
        print!("\n");
    }
}

/// Retorna un String con el numero con sufijo
fn sufijo(valor: f64) -> String {
    let mut nuevo_valor: f64 = valor;
    let mut suffix = "";
    if (valor).abs() > 999.0 {
        nuevo_valor = valor / 1000.0;
        suffix = "k";
    } else if (valor).abs() < 1e-9 {
        nuevo_valor = valor * 1e12;
        suffix = "p";
    } else if (valor).abs() < 1e-6 {
        nuevo_valor = valor * 1e9;
        suffix = "n";
    } else if (valor).abs() < 1e-3 {
        nuevo_valor = valor * 1e6;
        suffix = "μ";
    } else if (valor).abs() < 1.0 {
        nuevo_valor = valor * 1e3;
        suffix = "m";
    }
    return format!("{nuevo_valor:.3}{suffix}");
}
