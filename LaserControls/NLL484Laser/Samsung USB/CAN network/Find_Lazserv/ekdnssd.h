#ifndef EKDNSSD_H
#define EKDNSSD_H

#ifdef __cplusplus
extern "C" {
#endif
  int __stdcall ekdnssd_Init(const char *);
  int __stdcall ekdnssd_Get(char *ip, size_t ipbufsize, char *name, size_t namebufsize);
  int __stdcall ekdnssd_Deinit(void);
#ifdef __cplusplus
}
#endif

#endif //EKDNSSD_H
