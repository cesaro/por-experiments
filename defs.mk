
# traditional variables
CFLAGS:=-Wall -Wextra -std=c99 -O3
#CFLAGS:=-Wall -Wextra -std=c99 -pg
#CFLAGS:=-Wall -Wextra -std=c99 -g
CXXFLAGS:=-Wall -Wextra -std=c++11 -O3
#CXXFLAGS:=-Wall -Wextra -std=c++11 -pg
#CXXFLAGS:=-Wall -Wextra -std=c++11 -g
CPPFLAGS:=-I src/ -D_POSIX_C_SOURCE=200809L -D__STDC_LIMIT_MACROS -D__STDC_FORMAT_MACROS -D NDEBUG
LDFLAGS:=-dead_strip
#LDFLAGS:=

# source code
SRCS:=$(wildcard src/*.c src/*.cc src/*/*.c src/*/*.cc src/*/*/*.c src/*/*/*.cc)
SRCS:=$(filter-out %/cunf.cc, $(SRCS))
SRCS:=$(filter-out %/pep2dot.c, $(SRCS))
SRCS:=$(filter-out %/pep2pt.c, $(SRCS))

# do not remove files generated by lex or bison once you generate them
.SECONDARY: src/cna/spec_lexer.cc src/cna/spec_parser.cc

# source code containing a main() function
MSRCS:=$(wildcard src/cunf/cunf.cc src/pep2dot.c src/pep2pt.c)

# compilation targets
OBJS:=$(SRCS:.cc=.o)
OBJS:=$(OBJS:.c=.o)
MOBJS:=$(MSRCS:.cc=.o)
MOBJS:=$(MOBJS:.c=.o)
TARGETS:=$(MOBJS:.o=)

# dependency files
DEPS:=$(patsubst %.o,%.d,$(OBJS) $(MOBJS))

# list of nets for several tasks
#TEST_NETS:=$(shell tools/nets.sh test)
#TIME_NETS:=$(shell tools/nets.sh time)
#ALL_NETS:=$(shell tools/nets.sh no-huge)
#MCI_NETS:=$(shell tools/nets.sh mci)
#DEAD_NETS:=$(MCI_NETS)
#CNMC_NETS:=$(shell tools/nets.sh all | grep -v huge)

# define the toolchain
CROSS:=

LD:=$(CROSS)ld
CC:=$(CROSS)gcc
CXX:=$(CROSS)g++
CPP:=$(CROSS)cpp
LEX:=flex
YACC:=bison

%.d : %.c
	@echo "DEP $<"
	@set -e; $(CC) -MM -MT $*.o $(CFLAGS) $(CPPFLAGS) $< | \
	sed 's,\($*\)\.o[ :]*,\1.o $@ : ,g' > $@;

%.d : %.cc
	@echo "DEP $<"
	@set -e; $(CXX) -MM -MT $*.o $(CXXFLAGS) $(CPPFLAGS) $< | \
	sed 's,\($*\)\.o[ :]*,\1.o $@ : ,g' > $@;

%.cc : %.l
	@echo "LEX $<"
	@$(LEX) -o $@ $^

%.cc : %.y
	@echo "YAC $<"
	@$(YACC) -o $@ $^

# cancelling gnu make builtin rules for lex/yacc to c
# http://ftp.gnu.org/old-gnu/Manuals/make-3.79.1/html_chapter/make_10.html#SEC104
%.c : %.l
%.c : %.y

%.o : %.c
	@echo "CC  $<"
	@$(CC) $(CFLAGS) $(CPPFLAGS) -c -o $@ $<

%.o : %.cc
	@echo "CXX $<"
	@$(CXX) $(CXXFLAGS) $(CPPFLAGS) -c -o $@ $<

%.pdf : %.dot
	@echo "DOT $<"
	@dot -T pdf < $< > $@

%.svg : %.dot
	@echo "DOT $<"
	@dot -T svg < $< > $@

%.png : %.dot
	@echo "DOT $<"
	@dot -T png < $< > $@

%.jpg : %.dot
	@echo "DOT $<"
	@dot -T jpg < $< > $@

%.dot : %.pnml
	@echo "P2D $<"
	@src/pnml2dot.py < $< > $@

%.dot : %.ll_net
	@echo "P2D $<"
	@pep2dot $< > $@

%.pnml : %.cuf
	@echo "C2P $<"
	@src/cuf2pnml.py < $< > $@

%.ll_net : %.cuf
	@echo "C2P $<"
	@tools/cuf2pep.py < $< > $@

%.pt : %.ll_net
	@echo "P2PT $<"
	@src/pep2pt $< > $@

#%.ll_net : %.pt
#	@echo "PT2P $<"
#	@tools/pt2pep.py < $< > $@

#%.ll_net : %.mp
#	@echo "C2P $<"
#	@tools/mp2pep.py < $< > $@

%.unf.cuf : %.ll_net
	@echo "UNF $<"
	@cunf -i $< --save $@

%.mp.mp : %.unf.cuf
	@echo "MER $<"
	@tools/cmerge.py < $< > $@

%.unf.cuf.tr : %.ll_net
	tools/trt.py timeout=5000 t=cunf net=$< > $@

#%.unf.mci : %.ll_net
#	@echo "MLE $<"
#	@mole $< -m $@

%.ll_net : %.xml
	@echo "X2P $<"
	@tools/xml2pep.pl < $< > $@

%.ll_net : %.pnml
	@echo "P2P $<"
	@src/pnml2pep.py < $< > $@

%.ll_net : %.grml
	@echo "G2P $<"
	@tools/grml2pep.py < $< > $@

%.r : %.dot
	@echo "RS  $<"
	@tools/rs.pl $< > $@

%.ll_net : %.g
	@echo "X2P $<"
	@petrify -ip < $< | tools/stg2pep.py > $@

%.dot : %.mci
	@echo "M2D $<"
	@mci2dot $< > $@

