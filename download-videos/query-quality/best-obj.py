a = "aeroplane   0.82290 \
bicycle 0.78350 \
bird    0.70840 \
boat    0.52250 \
bottle  0.38720 \
bus 0.77770 \
car 0.71550 \
cat 0.89250 \
chair   0.44190 \
cow 0.73020 \
diningtable 0.55000 \
dog 0.87490 \
horse   0.80510 \
motorbike   0.80750 \
person  0.72030 \
pottedplant 0.35070 \
sheep   0.68270 \
sofa    0.65740 \
train   0.80410 \
tvmonitor   0.64240"



ss = []
for s in a.split(' '):
    if len(s) > 0:
        ss += [s]


n_objs = len(ss)/2

dd = {}
for obj in xrange(n_objs):
    idx = obj * 2
    ob = ss[idx]
    ac = float(ss[idx+1])
    dd[ob] = ac

for x in sorted(dd.items(), key=lambda x: x[1], reverse=True):
    print x


s = "0.18,0.29,0.28,0.26,0.08,0.12,0.06,0.4,0.09,0.15,0.25,0.33,0.25,0.23,0.16,0.16,0.35,0.25,0.14,0.33,0.22,0.07,0.28,0.13,0.15,0.27,0.19,0.3,0.2,0.12,0.44,0.45,0.13,0.21,0.12,0.2,0.3,0.15,0.07,0.31,0.11,0.26,0.08,0.09,0.37,0.17,0.36,0.4,0.36,0.17,0.17,0.1,0.22,0.19,0.31,0.22,0.22,0.22,0.19,0.22,0.13,0.2,0.17,0.18,0.09,0.3,0.37,0.23,0.2,0.19,0.09,0.17,0.18,0.34,0.02,0.04,0.32,0.28,0.16,0.06,0.28,0.3,0.12,0.24,0.14,0.1,0.11,0.26,0.38,0.21,0.26,0.23,0.18,0.19,0.06,0.15,0.11,0.23,0.07,0.06,0.18,0.14,0.06,0.12,0.18,0.34,0.14,0.28,0.2,0.06,0.44,0.26,0.13,0.33,0.14,0.24,0.15,0.2,0.18,0.12,0.17,0.33,0.2,0.19,0.35,0.35,0.13,0.18,0.15,0.29,0.24,0.26,0.03,0.13,0.47,0.09,0.26,0.2,0.25,0.18,0.16,0.31,0.18,0.18,0.23,0.17,0.46,0.1,0.32,0.23,0.32,0.24,0.06,0.21,0.27,0.16,0.11,0.36,0.19,0.12,0.15,0.19,0.2,0.07,0.13,0.18,0.15,0.18,0.03,0.29,0.17,0.18,0.33,0.18,0.3,0.24,0.2,0.16,0.13,0.2,0.32,0.33,0.11,0.26,0.2,0.24,0.25,0.16,0.31,0.19,0.37,0.16,0.12,0.14,0.22,0.27,0.19,0.07,0.14,0.4,0.3,0.0,0.36,0.22,0.14,0.06,0.29,0.32,0.22,0.25,0.31,0.28,0.1,0.1,0.12,0.27,0.23,0.24,0.24,0.51,0.06,0.28,0.26,0.39,0.32,0.15,0.2,0.51,0.19,0.08,0.13,0.17,0.07,0.13,0.05,0.01,0.12,0.08,0.02,0.19,0.15,0.12,0.12,0.1,0.11,0.06,0.14,0.14,0.17,0.16,0.21,0.05,0.1,0.14,0.11,0.07,0.32,0.35,0.2,0.09,0.13,0.02,0.06,0.15,0.07,0.19,0.19,0.08,0.17,0.19,0.21,0.07,0.2,0.16,0.14,0.1,0.18,0.05,0.14,0.07,0.1,0.33,0.22,0.31,0.1,0.16,0.13,0.03,0.16,0.24,0.26,0.32,0.12,0.14,0.12,0.22,0.35,0.17,0.08,0.18,0.1,0.26,0.42,0.29,0.21,0.17,0.21,0.19,0.44,0.35,0.22,0.24,0.21,0.15,0.17,0.03,0.24,0.18,0.19,0.17,0.13,0.16,0.27,0.06,0.14,0.14,0.17,0.15,0.28,0.02,0.38,0.11,0.12,0.2,0.73,0.4,0.15,0.29,0.13,0.21,0.14,0.1,0.29,0.2,0.29,0.24,0.37,0.19,0.38,0.38,0.3,0.19,0.19,0.33,0.24,0.59,0.02,0.01,0.16,0.18,0.06,0.11,0.08,0.23,0.15,0.25,0.27,0.0,0.74,0.6,0.77,0.12,0.56,0.22,0.6,0.24,0.3,0.62,0.75,0.45,0.22,0.16,0.11,0.14,0.14,0.14,0.08,0.1,0.13,0.13,0.14,0.16,0.13,0.11,0.08,0.16,0.33,0.08,0.24,0.05,0.08,0.21,0.19,0.08,0.1,0.14,0.26,0.04,0.11,0.13,0.03,0.14,0.1,0.24,0.13,0.04,0.12,0.15,0.15,0.21,0.05,0.12,0.19,0.13,0.01,0.14,0.12,0.25,0.24,0.09,0.07,0.14,0.06,0.07,0.05,0.11,0.09,0.07,0.16,0.07,0.11,0.14,0.21,0.23,0.2,0.1,0.12,0.15,0.05,0.11,0.26,0.09,0.07,0.06,0.13,0.28,0.45,0.22,0.28,0.2,0.3,0.1,0.28,0.18,0.24,0.29,0.26,0.26,0.39,0.18,0.4,0.15,0.17,0.16,0.19,0.35,0.38,0.26,0.44,0.21,0.16,0.09,0.37,0.34,0.66,0.21,0.48,0.14,0.21,0.42,0.28,0.39,0.29,0.11,0.3,0.23,0.23,0.1,0.19,0.14,0.35,0.28,0.16,0.44,0.53,0.48,0.2,0.36,0.52,0.49,0.37,0.24,0.44,0.4,0.48,0.37,0.19,0.14,0.36,0.01,0.57,0.24,0.36,0.34,0.16,0.34,0.2,0.35,0.39,0.42,0.57,0.33,0.37,0.27,0.55,0.57,0.09,0.3,0.24,0.26,0.52,0.48,0.29,0.16,0.14,0.51,0.17,0.19,0.21,0.25,0.22,0.42,0.02,0.1,0.14,0.31,0.08,0.05,0.18,0.17,0.35,0.81,0.23,0.08,0.19,0.1,0.09,0.12,0.26,0.48,0.2,0.07,0.11,0.52,0.36,0.05,0.15,0.45,0.15,0.47,0.52,0.23,0.39,0.44,0.41,0.37,0.09,0.6,0.14,0.09,0.39,0.03,0.59,0.33,0.47,0.27,0.42,0.11,0.3,0.21,0.12,0.18,0.3,0.14,0.38,0.28,0.13,0.12,0.24,0.3,0.26,0.48,0.16,0.34,0.33,0.16,0.18,0.21,0.51,0.18,0.19,0.18,0.12,0.39,0.29,0.14,0.17,0.16,0.19,0.19,0.31,0.38,0.32,0.44,0.3,0.25,0.2,0.25,0.22,0.09,0.07,0.13,0.07,0.02,0.08,0.12,0.12,0.11,0.16,0.14,0.17,0.31,0.28,0.33,0.07,0.13,0.25,0.28,0.32,0.06,0.28,0.26,0.16,0.33,0.26,0.28,0.2,0.27,0.26,0.21,0.5,0.36,0.41,0.36,0.24,0.77,0.08,0.07,0.15,0.12,0.13,0.05,0.1,0.14,0.14,0.24,0.2,0.12,0.1,0.17,0.09,0.06,0.1,0.51,0.18,0.15,0.14,0.4,0.06,0.11,0.1,0.2,0.21,0.61,0.26,0.22,0.12,0.25,0.22,0.35,0.21,0.16,0.09,0.05,0.29,0.13,0.04,0.26,0.15,0.16,0.21,0.14,0.2,0.12,0.14,0.3,0.18,0.14,0.08,0.36,0.33,0.23,0.13,0.12,0.14,0.2,0.06,0.09,0.13,0.13,0.2,0.15,0.19,0.1,0.08,0.11,0.21,0.24,0.28,0.22,0.31,0.5,0.14,0.27,0.18,0.29,0.2,0.43,0.34,0.16,0.3,0.27,0.04,0.3,0.35,0.46,0.11,0.25,0.31,0.21,0.08,0.41,0.25,0.25,0.2,0.24,0.32,0.15,0.27,0.22,0.44,0.4,0.25,0.2,0.24,0.24,0.34,0.2,0.08,0.23,0.24,0.2,0.13,0.31,0.05,0.21,0.48,0.33,0.52,0.38,0.14,0.3,0.12,0.22,0.23,0.25,0.15,0.24,0.26,0.53,0.23,0.08,0.08,0.31,0.41,0.13,0.36,0.37,0.6,0.46,0.09,0.28,0.36,0.28,0.3,0.2,0.48,0.31,0.2,0.2,0.45,0.12,0.28,0.09,0.2,0.24,0.44,0.18,0.21,0.2,0.18,0.27,0.25,0.16,0.2,0.25,0.49,0.18,0.06,0.48,0.53,0.08,0.1,0.19,0.28,0.49,0.13,0.28,0.51,0.2,0.13,0.34,0.34,0.46,0.32,0.26,0.27,0.33,0.61,0.14,0.26,0.33,0.37,0.37,0.34,0.15,0.42,0.08,0.26,0.44,0.38,0.06,0.28,0.33,0.32,0.07,0.05,0.19,0.38,0.37,0.17,0.89,0.09,0.2,0.59,0.21,0.19,0.27,0.13,0.18,0.32,0.3,0.1,0.22,0.23,0.21,0.35,0.15,0.38,0.4,0.26,0.29,0.17,0.13,0.23,0.26,0.28,0.12,0.19,0.16,0.37,0.06,0.51,0.37,0.29,0.13,0.2,0.45,0.33,0.29,0.31,0.22,0.21,0.25,0.41,0.1,0.42,0.34,0.41,0.19,0.25,0.12,0.24,0.36,0.42,0.28,0.29,0.15,0.25,0.31,0.45,0.29,0.18,0.12,0.4,0.04,0.42,0.64,0.14,0.38,0.12,0.07,0.16,0.55,0.24,0.31,0.38,0.38,0.54,0.22,0.26,0.32,0.13,0.34,0.36,0.25,0.38,0.68,0.33,0.16,0.14,0.16,0.48,0.35,0.23,0.34,0.41,0.35,0.14,0.14,0.4,0.28,0.13,0.21,0.19,0.43,0.56,0.25,0.11,0.35"

segs = s.split(",")


ds = {}
for i, line in enumerate(open('/home/t-yuche/caffe/data/ilsvrc12/synset_words.txt').readlines()):
    line = line.strip()
    ds[line] = float(segs[i])


counter = 0
for x in sorted(ds.items(), key=lambda x: x[1]):
    counter += 1
    if counter == 100:
        break
    print x
