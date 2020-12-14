# Title     : wilcox.R
# Objective : Wilcox diff analysis
# Created by: MingJia
# Created on: 2020/12/14
options(warn = -1)
.libPaths("/home/renchaobo/R/x86_64-unknown-linux-gnu-library/3.2")
library(optparse)
library(logging)
basicConfig()

option_list <- list(make_option(c("-i", "--input"),
                                type = "character",
                                help = "The input talbe"),
                    make_option(c("--group"),
                                type = "character",
                                help = "The group info file"),
                    make_option(c("-c", "--compare"),
                                type = "character",
                                help = "The compare group info like \"A&B,B&C\""),
                    make_option(c("-o", "--out"),
                                default = "./",
                                type = "character",
                                help = "The out put dir[default= %default]"))
opts <- parse_args(OptionParser(usage = "%prog [options]",
                                option_list = option_list,
                                description = "\nWilcox Diff analysis"),
                   positional_arguments = F)

#### Some Function ####
write_table <- function(df, index_name, file) {
  write.table(paste(index_name, "\t", sep = ""),
              append = F,
              quote = F,
              eol = "",
              row.names = F,
              col.names = F,
              file = file)
  write.table(df,
              append = T,
              quote = FALSE,
              sep = "\t",
              file = file)
}

#######################
loginfo("Read abundance file %s", opts$input)
df_all <- read.table(opts$input,
                     header = T,
                     row.names = 1,
                     check.names = F,
                     quote = "")
loginfo("Read group info file %s", opts$group)
group <- read.table(opts$group,
                    check.names = F,
                    sep = "\t",
                    quote = "",
                    stringsAsFactors = F)
colnames(group) <- c("Samples", "Groups")

compares <- unlist(strsplit(opts$compare, split = ","))
for (compare in compares) {
  loginfo("Deal compare %s", compare)
  union <- unlist(strsplit(compare, split = "&"))
  group1_samples <- group$Sample[group$Group == union[1]]
  group2_samples <- group$Sample[group$Group == union[2]]
  group_info <- c(group$Group[group$Group == union[1]], group$Group[group$Group == union[2]])

  result <- as.data.frame(df_all[, c(group1_samples, group2_samples)])
  result[paste(union[1], "mean", sep = '_')] <- apply(result[c(group1_samples)], 1, mean)
  result[paste(union[2], "mean", sep = '_')] <- apply(result[c(group2_samples)], 1, mean)
  result["log2fc"] <- log2(result[paste(union[2], "mean", sep = '_')] / result[paste(union[1], "mean", sep = '_')])
  result["p"] <- apply(result, 1, function(x) wilcox.test(x[group1_samples], x[group2_samples])$p.value)
  result["FDR"] <- p.adjust(result$p, method = "BH")
  file_result <- paste(opts$out, "/", union[1], "_vs_", union[2], ".wilcox.tsv", sep = "")
  write_table(result, "Index", file_result)
}


