pais(pietrop, joão).
pais(pietrop, clara).
pais(pietrop, francisco).
pais(pietrop, valéria).
pais(pietrop, ana).
pais(antonita, joão).
pais(antonita, clara).
pais(antonita, francisco).
pais(antonita, valéria).
pais(antonita, ana).
pais(ana, helena).
pais(ana, joana).
pais(joão, mário).
pais(helena, carlos).
pais(mário, carlos).
pais(clara, pietro).
pais(clara, enzo).
pais(jacynto, antonia).
pais(jacynto, francisca).
pais(claudia, antonia).
pais(claudia, francisca).
pais(luzia, jacynto).
pais(pablo, jacynto).
 
sexo(pietrop, m).
sexo(joão, m).
sexo(francisco, m).
sexo(mário, m).
sexo(carlos, m).
sexo(pietro,m).
sexo(enzo, m).
sexo(jacynto, m).
sexo(pablo, m).
sexo(antonita, f).
sexo(clara, f).
sexo(valéria, f).
sexo(ana, f).
sexo(helena, f).
sexo(joana, f).
sexo(fabiana, f).
sexo(francisca, f).
sexo(antonia, f).
sexo(cláudia, f).
sexo(luzia, f).
 
avoo(X,Y):- pais(X,A),
    pais(A,Y),
    sexo(X,m).
 
avoa(X,Y):- pais(X,A),
    pais(A,Y),
    sexo(X,f).
 
mae(X,Y):- pais(X,Y),
    sexo(X,f).
 
pai(X,Y):- pais(X,Y),
    sexo(X,m).
 
irmao(Y,Z):- pais(X,Y),
    pais(X,Z), 
    Z\==Y,
    sexo(Y,m).
 
irma(Y,Z):- pais(X,Y), 
    pais(X,Z),
    Y\==Z,
    sexo(Y,f).
 
tio(X, Y) :- irmao(X, Z), 
    pais(Z, Y),
    sexo(X, m).
 
tia(X,Y):- irma(X,Z),
    pais(Z,Y),
    sexo(X,f).
 
filho(X,Y):- pais(Y,X),
    sexo(X,m).
    
filha(X,Y):- pais(Y,X),
    sexo(X,f).
 
primo(X,Y):- pais(Z,X),
    pais(A,Y),
    irmao(Z,A),
    sexo(X,m).
 
prima(X,Y):- pais(Z,X),
    pais(A,Y),
    irmao(Z,A),
    sexo(X,f).
 
descendente(X,Y):- pais(Y,X);
    tio(Y,X);
	tia(Y,X);
    avoo(Y,X);
    X\==Y,
    avoa(Y,X).
 
 
ascendente(X, Y):- pais(X, Y);
    tio(X,Y);
	tia(X,Y);
    avoo(X,Y);
    X\==Y,
    avoa(X,Y).
 