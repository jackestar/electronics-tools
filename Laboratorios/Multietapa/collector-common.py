from sympy import symbols, Eq, solve
import numpy as np


def valor_proximo(valor, lista_valores):
	return min(lista_valores, key=lambda x: abs(x - valor))

commercial = {
	 1, 5, 6.4, 7.4, 10, 15, 27, 33, 40, 47, 50, 56, 82, 100, 150, 220, 330, 470, 390, 560, 1e3, 2e3, 2.2e3, 2.7e3, 3.3e3, 4.7e3, 3.8e3, 10e3, 22e3, 33e3, 47e3, 100e3, 220e3, 330e3, 680e3, 1e6, 1.8e6, 2.2e6, 6.2e6
}

ic, m, b, hie, rl, re, rb1, rb2, vth, rth, k, m, av, vcc, zo, rs, pal,ef=symbols('Ic m β Hie Rl Re Rb1 Rb2 Vth Rth K m Av Vcc Zo Rs pal ef')

eq = [
	ic - 10 * m,		# icq
	b - 210,		# b
	vcc - 20,
	hie - b * 26 * m / ic,	# hie
	rl - 10 * k,			# rl
	k - 1000,
	m - 1/1000,
	rs - 1 * k,
	vth - vcc * rb1 / (rb2 + rb1),
	rth - rb1*rb2/(rb1+rb2),
	rth - 0.1 * b * (re),
	# rth - 0.05 * b * (re),

	ic - vcc / ((re * rl) / (re + rl) + re),

	pal - rs*rth/(rs+rth),
	av - ef*(b+1)* (rl*re / (rl+re)) / (hie + (re * rl/(re+rl)) * (b + 1)),
	ef - rth*((b+1)*rl*re/(re+rl))/(rth+((b+1)*rl*re/(re+rl)))/(rth*((b+1)*rl*re/(re+rl))/(rth+((b+1)*rl*re/(re+rl)))+rs),
	ic - (vth - 0.7) / (rth/b + re),
	# av - .9,
	zo - (re * (pal + hie)/ (b + 1)) / (re + (pal + hie)/ (b + 1)),
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
	sol[solutions[0]][rl],
	sol[solutions[0]][hie],
	sol[solutions[0]][b],
	sol[solutions[0]][rb1],
	sol[solutions[0]][rb2],
	sol[solutions[0]][vth],
	sol[solutions[0]][vcc],
	sol[solutions[0]][re],
	sol[solutions[0]][zo],
]

# print(well[5])
rth, av, rl, hie, b, ic, icq, vth, re, zo, ef = symbols("rth Av Rl hie β Ic Icq Vth Re Zo ef")
new_eq = [
	rl - well[0],
	hie - well[1],
	b - well[2],
	rb1 - well[3],
	rb2 - well[4],
	vth - well[5],
	vcc - well[6],
	re - well[7],
	zo - well[8],
	rth - rb1 * rb2 / (rb1 + rb2),
	av - ef*(b+1)* (rl*re / (rl+re)) / (hie + (re * rl/(re+rl)) * (b + 1)),
	ef - rth*((b+1)*rl*re/(re+rl))/(rth+((b+1)*rl*re/(re+rl)))/(rth*((b+1)*rl*re/(re+rl))/(rth+((b+1)*rl*re/(re+rl)))+1000),
	icq  - vcc / ((re * rl) / (re + rl) + re),
	ic  - (vth - 0.7) / (rth/b + re),
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