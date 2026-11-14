"""Independent answer key based on direct enumeration or arithmetic identities."""
from fractions import Fraction as F
from itertools import combinations, product
from math import ceil, gcd


def independent(k, p, m):
    a,b,c,d,e=p
    match k:
        case 1:
            n=a+8; g=b+2; z=c%(n-1)+1
            return (sum(1 for i in range(n) for _ in range(g) if i<z) if m==1 else
                    ceil(F(z*g-1,g)) if m==2 else sum(g for i in range(z,n)))
        case 2:
            t,f,n,u=a+5,c+1,b+1,d+6
            return (F(t,t+f),1-F(n,n+t),1-F(f+n,t+f+n+u),1-F(u,u+f))[m]
        case 3:
            return ''.join(str(int(a*x+b*y>=c)) for x,y in ((0,0),(1,0),(0,1),(1,1))[m:]+((0,0),(1,0),(0,1),(1,1))[:m])
        case 4:
            return sum(all((a*x+b*y>=t)==bool(x and y if m%2 else x or y)
                           for x,y in product((0,1),repeat=2)) for t in range(a+b+2))
        case 5:
            n=a+6;step=b%4+2; start=c%step+1; other=(start+d-1)%n+1
            g=gcd(n,step)
            return n//g*(1+int(m%2 and (other-start)%g!=0))
        case 6:
            r,s=a+5,b+25; w=c%7+2
            v=F(w,10)*r+(1-F(w,10))*s
            return 100*(v-s)/(r-s) if m>=2 and r!=s else v
        case 7:
            values=[F(a+2+i,a+b+c+6) for i in range(c+2)]
            return (max if m%2 else min)(values)
        case 8:
            x=[bool(n%base) for n,base in zip(p,(7,5,3,3,2))]; y=[bool(i%4) for i in (b,c,d,e,a)]
            return sum((u and v,u or v,u and not v,u!=v)[m] for u,v in zip(x,y))
        case 9:
            return next(y for y in range(b+c+5) if y-(b+c+5-y)==b%5+1)
        case 10:
            v=F(a,a+b+c)
            return F(a,a+b)-v if m>=2 else v
        case 11:
            return next(k for k in range(1,100) if k*(max(a,b+2)+1-min(a,b+2))>e+1)
        case 12:
            return F(a+c,sum((a,b,c,d))+6)
        case 13:
            w=e%4+1;r=d%3+1
            return sum([w]*(a+3-min(a+3,b))+[-w]*min(a+3,b)+[-r]*c)
        case 14:
            return F(a+1+min(b+1,d%5+1),a+b+c+3)
        case 15:
            return F((a*c+b*d)**2,(a*a+b*b)*(c*c+d*d)) if m%2 else sum(z*z for z in (a-c,b-d))
        case 16:
            h=a+3;w=b+3;cut=min(h-1,c%5+1);ch=3 if m%2 else 1
            return h if m>=2 else sum(ch for _ in product(range(h-cut),range(w)))
        case 17:
            return F(6*(a+c)+6*b*(d%4+2),d%4+4)
        case 18:
            n=200+a;shift=b*3+15
            forward=lambda x:max(0,min(255,x+shift)-shift)
            return sum(forward(x)==255-shift for x in range(256)) if m>=2 and n+shift>255 else forward(n)
        case 19:
            den=d%6+3; alpha=F(e%(den-1)+1,den)
            return alpha if m%2 else 1-alpha
        case 20:
            h,w=a+3,b+3;i,j=c%h,d%w
            arr=[[int((y,x)==(i,j)) for x in range(w)] for y in range(h)]
            result=([row[::-1] for row in zip(*arr)] if m%2 else list(zip(*(row[::-1] for row in arr))))
            return str(next((y+1,x+1) for y,row in enumerate(result) for x,v in enumerate(row) if v))
        case 21:
            bits=((17*a+b)^(17*c+d))&1023
            return sum((e%6+2 if i>=5 else 1) for i in range(10) if bits&(1<<i))
        case 22:
            n=a%19+6;t=b%(n-2)+1
            return sum(1 for _ in combinations(range(t),c%(t+1)))*sum(1 for _ in combinations(range(t,n),d%(n-t+1)))
        case 23:
            arr=((a,b,c),(d,e,a+b),(b+c,c+d,d+e))
            values=[sum(arr[y+i][x+j]*(-1 if j==0 else 1) for i,j in product(range(2),repeat=2))
                    for y,x in product(range(2),repeat=2)]
            return (max if m%2 else min)(values)
        case 24:
            return F(b,b+d if m%2 else a+b)
        case 25:
            return 1-F(d,b+d)
        case 26:
            t=F(a%9+11,20);f=F(b%8+1,20); z=F(c%10+8,20)
            odds=z/(1-z)*f/t
            return odds/(1+odds)
        case 27:
            slope=F(c+1,d%5+1)
            return e+3+(b+2+m)*slope
        case 28:
            v=(b%5+1)*(a+c)+d+1
            return e+a+c-v
        case 29:
            m0=a%5+1;y=b+5;y2=y+m0+e%5-2;tol=d%4+1
            return sum(abs(x-y)<=tol and abs(x+m0-y2)<=tol for x in range(y-c%4-1,y+tol+1))
        case 30:
            return 0 if m>=2 else F(sum(x*x if m%2 else x for x in (a,b,c,d)),4)
        case 31:
            expanded=[a,b]+[c+15]*(d%6+2)
            return F(sum(expanded),len(expanded))
        case 32:
            u,v,x,y=a%7+2,b%7+1,c%6+1,d%6+1
            return F((y-v)*(y+v),(u-x)*(u+x))
        case 33:
            x=c%9+1; g=lambda t:(a%8+1)*t*t+(b%7+1)*t
            return F(g(x+1)-g(x-1),2)
        case 34:
            center=a%9+1;kappa=c%4+1;w=F(center+b%7+2)
            for _ in range(d%4+1):w-=F(2*kappa*(w-center),4*kappa)
            return w
        case 35:
            radius=F(1,b%5+2); k=a%9+1
            return (1-(-radius if m%2 else radius))/(2*k)
        case 36:
            successes=a%8+1
            return F(successes*(b+12-d-1)-(10-successes)*(c+2+d+1),10)
        case 37:
            values=(a+10,b+9,c+6)
            all_sets=[combo for n in (1,2) for combo in combinations(range(3),n)]
            pick=max(all_sets,key=lambda selected:sum(values[x] for x in selected)-(d+2 if selected==(0,1) else 0))
            return '·'.join('ABC'[j] for j in pick)+('만' if len(pick)==1 else '')
        case 38:
            return max(e,min((a+b+16)*x-b-1 for x in (F(c%5+1,10),F(c%5+d%4+2,10))))
        case 39:
            return ('학습','검증','최종 시험','외부 재평가')[m]
        case 40:
            values=[i for i in range(min(a+b,a+c)+1) if a+b+a+c-i<=a+b+c+d]
            return (max if m%2 else min)(values)
    raise ValueError(k)
