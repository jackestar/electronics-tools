from sympy import symbols, Eq, solve
import numpy as np


def valor_proximo(valor, lista_valores):
	return min(lista_valores, key=lambda x: abs(x - valor))

commercial = {
	 1, 5, 6.4, 7.4, 10, 15, 27, 33, 40, 47, 50, 56, 82, 100, 150, 220, 330, 470, 390, 560, 1e3, 2e3, 2.2e3, 2.7e3, 3.3e3, 4.7e3, 3.8e3, 10e3, 22e3, 33e3, 47e3, 100e3, 220e3, 330e3, 680e3, 1e6, 1.8e6, 2.2e6, 6.2e6
}

ic, m, b, hie, rl, rc, re, re1, re2, rb1, rb2, vth, rth, k, m, av, vcc=symbols('Ic m β Hie Rl Rc Re Re1 Re2 Rb1 Rb2 Vth Rth K m Av Vcc')

eq = [
	ic - 3 * m,		# icq
	b - 210,		# b
	av - int(input("Ganancia: ")),			# Vgain
	vcc - 20,
	hie - b * 26 * m / ic,	# hie
	rl - 10 * rc,
	rl - 10 * k,			# rl
	av - b * rc * rl / ((rc + rl) * (hie + re1 * (b + 1))),
	ic - vcc / ((rc * rl) / (rc + rl) + re1 + rc + re),
	re - re1 - re2,
	rth - 0.1 * b * (re1 + re2),
	vth - vcc * rb1 / (rb2 + rb1),
	rth - rb1*rb2/(rb1+rb2),
	k - 1000,
	m - 1/1000,
	ic - (vth - 0.7) / (rth/b + re)
]

sol = solve(eq)

if len(sol) == 0:
	print("No solution")
	exit()

solutions = []

for index,solution in enumerate(sol):
	print("\033[1;34mSolution:\033[0m")
	solutions.append(index)
	for key, value in solution.items():
		com = valor_proximo(value,commercial)
		suffix = "";
		if value > 999 or value < -999:
			value/=1000
			com/=1000
			suffix = "k"
		elif value < 1 and value > -1:
			value *= 1000
			com *=1000
			suffix = "m"

		if str(key)[0] == "R":
			if value < 0:
				print("Negative Resistance")
				solutions.pop()
				break
			print(f"\033[1;31m{key}:		{value:.2f}{suffix} ({com}{suffix})\033[0m")
		else:
			print(f"{key}:		{value:.2f}{suffix}")
	print()
print()

for index in solutions:
	solution = sol[index]
	for key, v in solution.items():
		value = v
		if str(key)[0] == "R" and not "th" in str(key):
			c = valor_proximo(value,commercial)
			com = c
			suffix = "";
			if value > 999 or value < -999:
				value/=1000
				com/=1000
				suffix = "k"
			elif value < 1 and value > -1:
				value *= 1000
				com *=1000
				suffix = "m"
			new = input(f"\033[1;32m{key}:		{value:.2f}{suffix} ({com}{suffix}?): \033[0m") or float(c)
			# print(type(new))
			if type(new) != type(0.1):
				if "k" in new:
					new = int(new.removesuffix("k"))*1000
				elif "m" in new:
					new = int(new.removesuffix("m"))/1000

			sol[index][key] = int(new)

well = [
	sol[0][rl],
	sol[0][rc],
	sol[0][hie],
	sol[0][re1],
	sol[0][b],
	sol[0][rb1],
	sol[0][rb2],
	sol[0][vth],
	sol[0][vcc],
	sol[0][re2],
]

rth, av, rl ,rc, hie, re1, b, ic, icq, vth, re2 = symbols("rth Av Rl Rc hie Re1 β Ic Icq Vth Re2")
new_eq = [
	rl - well[0],
	rc - well[1],
	hie - well[2],
	re1 - well[3],
	b - well[4],
	rb1 - well[5],
	rb2 - well[6],
	vth - well[7],
	vcc - well[8],
	re2 - well[9],
	rth - rb1 * rb2 / (rb1 + rb2),
	av - b * rc * rl / ((rc + rl) * (hie + re1 * (b + 1))),
	ic - (vth - 0.7) / (rth/b + re1 + re2),
	icq - vcc / (rc * rl / (rc + rl) + re1 + re2 + re1)
]

new_sol = solve(new_eq)

print("\033[1;34m\nPractical Values:\033[0m")
for solution in new_sol:
	for key, value in solution.items():
		if "Av" in str(key) or "Ic" in str(key):
			com = valor_proximo(value,commercial)
			suffix = "";
			if value > 999 or value < -999:
				value/=1000
				com/=1000
				suffix = "k"
			elif value < 1 and value > -1:
				value *= 1000
				com *=1000
				suffix = "m"
	
			print(f"{key}:		{value:.2f}{suffix}")