
include defs.mk

.PHONY: all tags

all : execute

execute :
	-./src/test.py a22.ll_net
	#-./src/test.py abp.ll_net

tags : $(SRCS)
	ctags -R src/

-include $(DEPS)

