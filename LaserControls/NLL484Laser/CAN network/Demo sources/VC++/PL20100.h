#ifndef __PL20100_H
#define __PL20100_H

extern double attenuation, reprate;

void Connect(void);
void Run(void);
void Stop(void);
void SetAttenuation(double f);
void SetRepRate(double f);

#endif